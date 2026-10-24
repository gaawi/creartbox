#!/usr/bin/env python3
"""The page for someone who wants to hear classical music in New York.

    python3 tools/build_guide.py            # write classical-concerts-nyc.html
    python3 tools/build_guide.py --check    # fail if it is out of date

The calendar answers "what is on". This page answers everything around
it: where the hall is, how to get there, what time a concert starts,
how long it runs, what a seat costs and what the evening is like. Those
are the questions people type into a search box, and the ones an
assistant has to answer from somewhere.

The season dates come from the New York Series rows of concerts.html,
so the page follows the calendar: when a concert is archived it leaves
this page too. Everything else is written here, and every fact in it is
either on another page of the site or was checked against the source
named in the comment beside it.
"""

import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_block                                       # noqa: E402
from build_presenters import foot, head                # noqa: E402

OUT = "classical-concerts-nyc.html"
INDEX = "concerts.html"
SITE = "https://creartbox.nyc"

TITLE = "Classical concerts in New York - CreArtBox at The DiMenna Center"
DESC = ("Chamber music in Midtown Manhattan: the CreArtBox New York Series at The DiMenna "
        "Center, 450 West 37th Street. Dates, start times, running times and ticket prices.")

ROW_RE = re.compile(r'<tr[^>]*data-concert-series="NYS"[^>]*>.*?</tr>', re.S)
HREF_RE = re.compile(r'class="title-cell"><a href="([^"]+)"')
TITLE_RE = re.compile(r'class="title-cell"><a[^>]*>(.*?)</a>', re.S)
NUM_RE = re.compile(r'<span class="num">(\d+)</span>')
MONTH_RE = re.compile(r'<span style="display:block;font-size:14px[^"]*">([^<]*)</span>')
TIME_RE = re.compile(r'<span class="row-time">([^<]*)</span>')
WHERE_RE = re.compile(r'<td class="where">(.*?)</td>', re.S)


def plain(fragment):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def dates():
    """The New York Series rows of the calendar, in calendar order."""
    src = open(INDEX, encoding="utf-8").read()
    out = []
    for row in ROW_RE.findall(src):
        href = HREF_RE.search(row)
        if not href:
            continue
        num, month = NUM_RE.search(row), MONTH_RE.search(row)
        when = TIME_RE.search(row)
        where = WHERE_RE.search(row)
        out.append({
            "path": href.group(1),
            "title": plain(TITLE_RE.search(row).group(1)),
            "date": "{} {}".format(num.group(1) if num else "",
                                   month.group(1) if month else "").strip(),
            "time": plain(when.group(1)) if when else "",
            "where": plain(where.group(1).split("<br>")[0]) if where else "",
        })
    return out


FAQ = [
    ("Where does CreArtBox perform in New York?",
     "At The DiMenna Center for Classical Music, 450 West 37th Street, between Ninth and "
     "Tenth Avenues in Midtown Manhattan. The whole New York Series is given there. The "
     "ensemble also tours, and those dates are on the calendar with their own venues."),
    ("How do I get to The DiMenna Center?",
     "By subway, the A, C and E stop at 34th Street&#8211;Penn Station and the 7 at 34th "
     "Street&#8211;Hudson Yards; both are a few minutes&#x27; walk. The entrance is on West "
     "37th Street."),
    ("What time do concerts start?",
     "The four New York Series productions of the 2026/27 season each start at 7:30 pm. "
     "Touring dates and Festival ADAR keep their "
     "own times, which are on each concert page."),
    ("How much are tickets?",
     "Seats are sold through Eventbrite and each concert page carries its own link and "
     "prices. Currents, on 30 October 2026, starts at $15. A Premium ticket puts you in the "
     "closest rows to the players, with a small treat on the night."),
    ("How long is a concert, and is there an intermission?",
     "Currents runs about an hour and is played without an intermission. Running times are "
     "given on the concert page once the programme is set."),
    ("What kind of music will I hear?",
     "Chamber music, with the standard repertoire and new work in the same evening: in "
     "2026/27, Brahms and both Schumanns share a programme with Eric Moe, and Stravinsky "
     "shares one with the world premiere of Hannah Selin&#x27;s <em>Tectonic Lullaby</em>. "
     "Eleven works this season reached the programme through the ensemble&#x27;s open call "
     "for scores. Most productions carry something besides the music, usually video art or "
     "stage design made for the room."),
    ("Who plays?",
     "The core ensemble is flute, violin, viola, cello and piano &#8211; Guillermo Laporta, "
     "Emilie-Anne Gendron, Matthew Cohen, Julia Yang and Josefina Urraca &#8211; with guest "
     "musicians when a programme asks for them. Each concert page lists who is playing that "
     "night."),
    ("Can I see what CreArtBox has played before?",
     "Yes. The archive holds every performance since 2013, with programmes and photographs, "
     "and the repertoire page lists every work the ensemble has played."),
]


def faq_block():
    items = "\n".join(
        '      <details><summary><span style="flex:1">{q}</span>'
        '<span class="ind"></span></summary><p>{a}</p></details>'.format(q=q, a=a)
        for q, a in FAQ)
    return """
<section class="section tinted">
  <div class="wrap two-col">
    <div>
      <span class="label">Before you come</span>
      <h2 class="h-title" style="margin-top:14px">Questions we are <em>asked</em>.</h2>
    </div>
    <div class="faq">
{items}
    </div>
  </div>
</section>
""".format(items=items)


def dates_block(rows):
    if not rows:
        return ""
    lines = "\n".join(
        '        <li><a href="{path}">'
        '<span class="un-date">{date}</span>'
        '<span class="un-title">{title}</span>'
        '<span class="un-where">{where}</span></a></li>'.format(
            path=r["path"], date=r["date"], title=html.escape(r["title"]),
            where=", ".join(x for x in (r["where"], r["time"]) if x))
        for r in rows)
    return """
    <div class="upnext" style="margin-top:8px">
      <div class="upnext-head"><span class="label">New York Series</span><hr class="rule"></div>
      <ul class="upnext-list">
{lines}
      </ul>
    </div>
""".format(lines=lines)


def page():
    rows = dates()
    body = """
<section class="section">
  <div class="wrap">
    <div class="page-folio-head">
      <span class="label">Coming to a concert</span>
      <hr class="rule" style="width:100%">
      <span class="label ital">New York City</span>
    </div>
    <h1 class="h-mast" style="margin-top:24px;max-width:18ch;">Classical concerts in <em>New York</em>.</h1>
    <p class="lede" style="margin-top:36px;max-width:62ch">
      CreArtBox is a chamber music ensemble founded in New York in 2013. Its New York
      Series runs from autumn to spring at The DiMenna Center for Classical Music, in
      Midtown Manhattan, and the four productions of this season each start at 7:30 pm.
      The calendar says
      what is on. This page is the practical half: the hall, the way in, how long an
      evening lasts and what a seat costs.
    </p>

    <div class="calls-apply" style="margin-top:28px">
      <a class="btn btn-ticket" href="concerts.html" data-cb-track="calendar" data-cb-where="guide">See the calendar <span class="ar">&#8594;</span></a>
      <span class="calls-apply-note">Tickets are sold through Eventbrite, from the page of each concert.</span>
    </div>
{dates}
    <hr class="rule" style="margin-top:44px">

    <div class="two-col-wide" style="padding:36px 0 0">
      <div><h2 class="h-title">The <em>hall</em>.</h2></div>
      <div>
        <p class="body-l" style="margin:0">
          The New York Series is given at <strong>The DiMenna Center for Classical
          Music</strong>, 450 West 37th Street, between Ninth and Tenth Avenues in Midtown
          Manhattan. It is a hall built for classical music, and it is where the ensemble
          gives its New York Series.
        </p>
        <p class="body-l">
          By subway, the A, C and E stop at 34th Street&#8211;Penn Station and the 7 at
          34th Street&#8211;Hudson Yards, both a few minutes&#x27; walk. For group rates,
          accessibility or press tickets, write to
          <a href="mailto:info@creartbox.nyc">info@creartbox.nyc</a>.
        </p>
      </div>
    </div>

    <hr class="rule" style="margin-top:36px">

    <div class="two-col-wide" style="padding:36px 0 0">
      <div><h2 class="h-title">The <em>evening</em>.</h2></div>
      <div>
        <p class="body-l" style="margin:0">
          A CreArtBox programme puts the standard repertoire and new music in the same
          hour. In the 2026/27 season Brahms and both Schumanns share an evening with
          Eric Moe; Stravinsky shares one with the world premiere of Hannah Selin&#x27;s
          <em>Tectonic Lullaby</em>; and one production, <em>Pressure and Release</em>, is
          given over entirely to seven composers chosen through the ensemble&#x27;s open
          call for scores. Eleven works this season arrived that way.
        </p>
        <p class="body-l">
          Most productions carry something besides the music: video art, stage design or
          lighting made for the room. <em>Currents</em>, on 30 October 2026, runs about an
          hour and is played without an intermission.
        </p>
        <div style="display:flex;gap:10px;margin-top:22px;flex-wrap:wrap">
          <a class="btn" href="concerts.html">Calendar <span class="ar">&#8594;</span></a>
          <a class="btn" href="archive.html">Everything played since 2013</a>
          <a class="btn" href="repertoire.html">The repertoire</a>
          <a class="btn" href="about.html">About the ensemble</a>
        </div>
      </div>
    </div>
  </div>
</section>
{faq}""".format(dates=dates_block(rows), faq=faq_block())
    return head(TITLE, DESC, SITE + "/" + OUT) + body + foot()


def main():
    check = "--check" in sys.argv
    wanted = page()
    current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    bare = seo_block.strip(current)
    if bare == wanted:
        print("the New York guide is current")
        return 0
    if check:
        print("the New York guide is out of date\n\nRun: python3 tools/build_guide.py")
        return 1
    open(OUT, "w", encoding="utf-8").write(seo_block.carry(current, wanted))
    print("wrote %s (%d New York dates)" % (OUT, len(dates())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
