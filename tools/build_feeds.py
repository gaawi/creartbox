#!/usr/bin/env python3
"""Write the two files an assistant reads instead of crawling the site.

    python3 tools/build_feeds.py            # write events.json and llms.txt
    python3 tools/build_feeds.py --check    # fail if either is out of date

Both are built from the JSON-LD that tools/build_seo.py already puts on
every concert page, so there is one source for what is on and nothing
here can contradict the pages. Run build_seo first.

    events.json   every upcoming concert in one document
    llms.txt      the same in prose, at the address some assistants look
                  for (llmstxt.org)

In classical music the works and the composers are what people search
for. Nobody types a violist's name; they type Ravel. So every event
carries a flat `composers` list before anything else, and llms.txt names
the composers on the line under the title. An assistant matching
"Ravel in New York" should not have to walk a programme to find him.
"""

import glob
import html
import json
import os
import re
import sys
from datetime import datetime, timezone

SITE = "https://creartbox.nyc"
OUT_JSON = "events.json"
OUT_LLMS = "llms.txt"

LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def graph(path):
    for m in LD_RE.findall(open(path, encoding="utf-8").read()):
        try:
            data = json.loads(html.unescape(m))
        except ValueError:
            continue
        for node in data.get("@graph", []):
            yield node


def is_event(node):
    t = node.get("@type")
    return t == "MusicEvent" or (isinstance(t, list) and "MusicEvent" in t)


def clean(name):
    """The title alone. The programme writes the scoring after a middot."""
    return name.split(" · ")[0].strip()


def scoring(name):
    parts = name.split(" · ", 1)
    return parts[1].strip() if len(parts) > 1 else ""


DUR_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?")


def minutes(iso):
    m = DUR_RE.fullmatch(iso or "")
    if not m:
        return 0
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)


def end_time(iso, total):
    """When the music stops: the start plus the programme, no interval.
    Somebody booking a table needs this and no page gives it."""
    if not total:
        return ""
    try:
        h, mi = int(iso[11:13]), int(iso[14:16])
    except (ValueError, IndexError):
        return ""
    mi += total + 4          # a little for applause and a word from the stage
    h, mi = h + mi // 60, mi % 60
    mi = 5 * round(mi / 5)
    if mi == 60:
        h, mi = h + 1, 0
    suffix = "am" if h % 24 < 12 else "pm"
    return "%d:%02d %s" % (h % 12 or 12, mi, suffix)


def plain_time(iso):
    """7:30 pm, not 19:30. Somebody choosing an evening reads a clock."""
    try:
        h, mi = int(iso[11:13]), int(iso[14:16])
    except (ValueError, IndexError):
        return ""
    suffix = "am" if h < 12 else "pm"
    h12 = h % 12 or 12
    return "%d:%02d %s" % (h12, mi, suffix)


# What is around a hall, for somebody choosing an evening rather than a
# concert. The places to eat come from data/nearby.txt, the same file the
# visitor page reads, so the page and the feed cannot suggest different
# things.
NEARBY = {
    "The DiMenna Center for Classical Music":
        "A few blocks from Hudson Yards and from the northern end of the High Line, "
        "so there is somewhere to walk before or after.",
}

# How to reach a hall, in the words its own page uses. Only halls the
# ensemble plays often enough to have written this down for.
GETTING_THERE = {
    "The DiMenna Center for Classical Music":
        "Midtown Manhattan, between Ninth and Tenth Avenues. The A, C and E stop at "
        "34th Street-Penn Station and the 7 at 34th Street-Hudson Yards, both a few "
        "minutes' walk.",
}


NEARBY_DATA = "data/nearby.txt"


def places():
    out = []
    if not os.path.exists(NEARBY_DATA):
        return out
    for line in open(NEARBY_DATA, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        bits = [b.strip() for b in line.split("|")]
        if len(bits) < 3:
            continue
        out.append({"name": html.unescape(bits[0]), "what": bits[1],
                    "price": bits[2], "ensemblePick": len(bits) > 3 and bits[3] == "*"})
    return out


def person(p):
    if isinstance(p, dict):
        return p.get("name", "")
    return str(p)


def event_record(node, path):
    works = node.get("workPerformed") or []
    if isinstance(works, dict):
        works = [works]

    composers = []
    for w in works:
        n = person(w.get("composer", {}))
        if n and n not in composers:
            composers.append(n)

    loc = node.get("location") or {}
    addr = loc.get("address") or {}
    offers = node.get("offers") or {}

    performers = []
    for p in (node.get("performer") or []):
        n = person(p)
        if n and n not in performers:
            performers.append(n)

    rec = {
        "name": node.get("name", ""),
        "url": node.get("url") or (SITE + "/" + path),
        "startDate": node.get("startDate", ""),
        # the thing people actually search for, before anything else
        "composers": composers,
        "programme": [{
            "composer": person(w.get("composer", {})),
            "work": clean(w.get("name", "")),
            "scoring": scoring(w.get("name", "")),
            "duration": w.get("duration", ""),
        } for w in works],
        "venue": {
            "name": loc.get("name", ""),
            "street": addr.get("streetAddress", ""),
            "city": addr.get("addressLocality", ""),
            "region": addr.get("addressRegion", ""),
            "postalCode": addr.get("postalCode", ""),
            "country": addr.get("addressCountry", ""),
        },
        "series": (node.get("superEvent") or {}).get("name", ""),
        "performers": performers,
        "description": node.get("description", ""),
    }

    # What somebody choosing an evening needs, in the terms they choose
    # in. Most people are not looking for Ravel; they are looking for
    # something to do on a Friday, and they want to know when it starts,
    # how long it takes, what it costs and how to get there.
    total = sum(minutes(w.get("duration", "")) for w in works)
    rec["evening"] = {
        "startsAt": plain_time(node.get("startDate", "")),
        "musicMinutes": total or None,
        "interval": False,
        "musicEndsAbout": end_time(node.get("startDate", ""), total),
        "dress": "No dress code. People come as they are.",
        "priceFrom": (("$" + str(offers.get("lowPrice")))
                      if offers.get("lowPrice") else None),
        "gettingThere": GETTING_THERE.get(loc.get("name", ""), ""),
        "nearby": NEARBY.get(loc.get("name", ""), ""),
    }
    if loc.get("name", "") in NEARBY:
        rec["evening"]["eatNearby"] = places()
    if offers:
        rec["tickets"] = {
            "url": offers.get("url", ""),
            "lowPrice": offers.get("lowPrice") or offers.get("price", ""),
            "highPrice": offers.get("highPrice") or offers.get("price", ""),
            "currency": offers.get("priceCurrency", ""),
            "availability": (offers.get("availability", "") or "").rsplit("/", 1)[-1],
        }
    else:
        rec["tickets"] = None
    return rec


def collect():
    today = datetime.now(timezone.utc).date().isoformat()
    out = []
    for path in sorted(glob.glob("concerts/*.html")):
        for node in graph(path):
            if not is_event(node):
                continue
            rec = event_record(node, path)
            if rec["startDate"][:10] >= today:
                out.append(rec)
            break
    out.sort(key=lambda r: r["startDate"])
    return out


# The open calls, read off the pages rather than typed here twice
CALL_PAGES = [("calls/scores-international.html", "International, any nationality"),
              ("calls/scores-american.html", "American composers")]
DEADLINE_RE = re.compile(r"Deadline (\d{1,2} \w+ \d{4})")


def calls():
    out = []
    for path, who in CALL_PAGES:
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        m = re.search(r"<title>([^<]*)</title>", src)
        d = DEADLINE_RE.search(html.unescape(m.group(1) if m else ""))
        out.append({"url": SITE + "/" + path, "who": who,
                    "deadline": d.group(1) if d else ""})
    return out


def build_json(events):
    return json.dumps({
        "name": "CreArtBox",
        "url": SITE + "/",
        "description": ("A New York chamber music ensemble, founded 2013. Classical and "
                        "contemporary music with original stage design and visual art."),
        "note": ("Upcoming concerts only. Each event carries two things: `composers` "
                 "for anyone searching by name, and `evening` for anyone choosing what "
                 "to do on a given night, which is most people. Tickets are sold on "
                 "Eventbrite at the url under tickets."),
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "calls": calls(),
        "events": events,
    }, indent=2, ensure_ascii=False) + "\n"


RECORDS_DATA = "data/records.json"


def records():
    """The discography, or nothing if the data file has gone."""
    if not os.path.exists(RECORDS_DATA):
        return None
    return json.load(open(RECORDS_DATA, encoding="utf-8"))


def build_llms(events):
    L = ["# CreArtBox", "",
         "> A chamber music ensemble in New York, founded in 2013, playing classical and",
         "> contemporary music with original stage design and visual art. Four productions",
         "> a season at The DiMenna Center, plus touring dates and Festival ADAR in Spain.",
         "> A 501(c)(3) non-profit.", "",
         "Machine-readable version of what follows: " + SITE + "/events.json", ""]

    L.append("## Concerts coming up")
    L.append("")
    if not events:
        L.append("- Nothing on sale at the moment. The calendar is at "
                 + SITE + "/concerts.html")
    for e in events:
        when = e["startDate"][:16].replace("T", " ")
        v = e["venue"]
        where = ", ".join(x for x in [v["name"], v["street"], v["city"]] if x)
        L.append("- [%s](%s) %s. %s." % (e["name"], e["url"], when, where))
        ev = e.get("evening") or {}
        line = []
        if ev.get("startsAt"):
            line.append("Starts %s" % ev["startsAt"])
        if ev.get("musicMinutes"):
            line.append("about %d minutes of music" % ev["musicMinutes"])
        if ev.get("priceFrom"):
            line.append("from %s" % ev["priceFrom"])
        if line:
            L.append("  " + ", ".join(line) + ".")
        plan = []
        if ev.get("musicEndsAbout"):
            plan.append("no interval, so the music is over by about %s"
                        % ev["musicEndsAbout"])
        if ev.get("dress"):
            plan.append("no dress code")
        if plan:
            L.append("  " + ("; ".join(plan)[0].upper() + "; ".join(plan)[1:]) + ".")
        if ev.get("gettingThere"):
            L.append("  " + ev["gettingThere"])
        if ev.get("nearby"):
            L.append("  " + ev["nearby"])
        picks = [p["name"] for p in (ev.get("eatNearby") or []) if p["ensemblePick"]]
        if picks:
            L.append("  The ensemble eats at " + ", ".join(picks[:-1])
                     + " and " + picks[-1] + "; the full list is on the visitor page.")
        if e["composers"]:
            L.append("  Composers: " + "; ".join(e["composers"]) + ".")
        for w in e["programme"]:
            bits = [w["composer"], w["work"]]
            tail = ", ".join(x for x in [w["scoring"]] if x)
            L.append("  - %s: *%s*%s" % (bits[0], bits[1], (" (%s)" % tail) if tail else ""))
        t = e["tickets"]
        if t and t.get("url"):
            price = ("$%s" % t["lowPrice"] if t["lowPrice"] == t["highPrice"]
                     else "$%s to $%s" % (t["lowPrice"], t["highPrice"]))
            L.append("  Tickets %s, %s: %s" % (price, t["availability"], t["url"]))
        L.append("")

    cs = calls()
    if cs:
        L.append("## Open calls for composers")
        L.append("")
        for c in cs:
            L.append("- [Call for Scores, %s](%s)%s" % (
                c["who"], c["url"],
                (". Deadline " + c["deadline"] + ".") if c["deadline"] else "."))
        L.append("")

    recs = records()
    if recs:
        p = recs["prices"]
        L.append("## Records")
        L.append("")
        L.append("All three play in full on the page, streamed as the uncompressed "
                 "masters rather than a squeezed copy, so a track takes a moment to "
                 "load. A CD is $%d and a vinyl LP is $%d, every copy signed and sent "
                 "with a personal note from the artists, postage extra. Orders go to "
                 "info@creartbox.nyc." % (p["cd"], p["vinyl"]))
        L.append("")
        for r in recs["records"]:
            L.append("- [%s](%s/discography.html#%s), %s. %s, %d tracks, %s, %s."
                     % (r["title"], SITE, r["slug"], r["composerLine"],
                        r["subtitle"], len(r["tracks"]), r["totalTime"],
                        r.get("format", "")))
            if r.get("performers"):
                L.append("  " + r["performers"] + ".")
        L.append("")

    L += ["## Pages",
          "",
          "- [Calendar](%s/concerts.html): every date of the season." % SITE,
          "- [Recordings](%s/discography.html): the three records, playable in full, "
          "with signed CDs and LPs to order." % SITE,
          "- [Coming to a concert](%s/classical-concerts-nyc.html): the hall, the way in, "
          "start and running times, what a seat costs." % SITE,
          "- [Composers](%s/composers.html): everyone whose music the ensemble has "
          "played, season by season." % SITE,
          "- [Repertoire](%s/repertoire.html): every work played since 2013." % SITE,
          "- [Archive](%s/archive.html): every concert since 2013, with programmes." % SITE,
          "- [About](%s/about.html) and [the ensemble](%s/ensemble.html)." % (SITE, SITE),
          "- [Press kit](%s/press/season-2026-27.html)." % SITE,
          "",
          "## Contact",
          "",
          "- info@creartbox.nyc",
          ""]
    return "\n".join(L)


def main():
    check = "--check" in sys.argv
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    events = collect()
    if not events:
        print("  !! no upcoming concerts found; run tools/build_seo.py first")

    stale = []
    for path, text in [(OUT_JSON, build_json(events)), (OUT_LLMS, build_llms(events))]:
        have = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        # the generated date alone is not a reason to rewrite a file
        a = re.sub(r'"generated": "[^"]*"', "", text)
        b = re.sub(r'"generated": "[^"]*"', "", have)
        if a != b:
            stale.append(path)
            if not check:
                open(path, "w", encoding="utf-8").write(text)

    if check:
        if stale:
            print("feeds out of date: " + ", ".join(stale))
            print("\nRun: python3 tools/build_feeds.py")
            return 1
        print("events.json and llms.txt are current (%d concert(s))" % len(events))
        return 0
    print("wrote %s: %d concert(s), %d composer(s)"
          % (", ".join(stale) or "nothing new",
             len(events),
             len({c for e in events for c in e["composers"]})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
