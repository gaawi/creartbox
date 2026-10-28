#!/usr/bin/env python3
"""Write the Google Ads Editor import files for the Ad Grant, and check
every piece of copy against Google's character limits before it goes.

    python3 docs/ads/build_ads.py

Four CSVs land next to this script, in the order Google Ads Editor
wants them: campaigns, ad groups, keywords, ads. Sitelinks are in a
fifth. Nothing here touches the live account: the files are imported by
hand, and reviewed on screen before anything is enabled.

Everything the ads claim is on the site and was checked there: the date
and time of the concert, the venue, the $15 starting price read from
the Eventbrite listing, the deadline and the $20 fee of the calls, the
founding year. No ad promises anything the site does not say.
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://creartbox.nyc"

# Google's limits for a responsive search ad and its assets
LIMITS = {"headline": 30, "description": 90, "path": 15,
          "sitelink": 25, "sitelink_desc": 35}

# The daily figures add up to the $329 a day the grant allows. The calls
# campaign stops being useful after 15 December; move its share to the
# concerts campaign then.
CAMPAIGNS = [
    {"name": "CB | Concerts | New York", "budget": "170.00",
     "locations": "New York, NY, United States; Jersey City, NJ, United States",
     "note": "Radius around New York City. Season dates and ticket pages."},
    {"name": "CB | Calls for Scores | International", "budget": "70.00",
     "locations": "United States; Canada; United Kingdom; Ireland; Australia; Spain; Germany; France",
     "note": "CA1/2026. Until 15 December 2026."},
    {"name": "CB | Calls for Scores | American", "budget": "60.00",
     "locations": "United States",
     "note": "CA2/2026. Until 15 December 2026."},
    {"name": "CB | Brand", "budget": "29.00",
     "locations": "United States; Spain; Canada; United Kingdom",
     "note": "Protects the account click-through rate, which has to stay above 5%."},
]

# (campaign, ad group, [keywords], final url)
# Phrase and exact only. No broad match: on a grant account a broad
# keyword buys irrelevant clicks and the click-through rate is what the
# account lives or dies by. No single-word keywords, which the policy
# forbids outside its own exceptions.
AD_GROUPS = [
    ("CB | Concerts | New York", "Chamber music NYC", [
        ('"chamber music concerts new york"', "Phrase"),
        ('"chamber music nyc tickets"', "Phrase"),
        ('"chamber music new york city"', "Phrase"),
        ('[chamber music concert new york]', "Exact"),
        ('"chamber music concerts this weekend nyc"', "Phrase"),
     ], SITE + "/classical-concerts-nyc.html"),

    ("CB | Concerts | New York", "Classical concerts NYC", [
        ('"classical music concerts new york city"', "Phrase"),
        ('"classical concerts in manhattan"', "Phrase"),
        ('"live classical music midtown manhattan"', "Phrase"),
        ('[classical concerts nyc]', "Exact"),
        ('"classical music events new york this week"', "Phrase"),
     ], SITE + "/classical-concerts-nyc.html"),

    ("CB | Concerts | New York", "DiMenna Center", [
        ('"dimenna center concerts"', "Phrase"),
        ('"dimenna center for classical music events"', "Phrase"),
        ('"concerts at the dimenna center"', "Phrase"),
        ('[dimenna center classical music]', "Exact"),
     ], SITE + "/classical-concerts-nyc.html"),

    ("CB | Concerts | New York", "Currents, 30 October", [
        ('"brahms concert new york"', "Phrase"),
        ('"clara schumann concert new york"', "Phrase"),
        ('"schumann piano quartet concert nyc"', "Phrase"),
        ('"piano quintet concert new york"', "Phrase"),
     ], SITE + "/concerts/currents-2026.html"),

    ("CB | Calls for Scores | International", "Call for scores", [
        ('"call for scores 2026"', "Phrase"),
        ('"open call for scores"', "Phrase"),
        ('"call for scores chamber music"', "Phrase"),
        ('[call for scores for composers]', "Exact"),
        ('"call for scores deadline december"', "Phrase"),
     ], SITE + "/calls/scores-international.html"),

    ("CB | Calls for Scores | International", "Composer opportunities", [
        ('"opportunities for composers"', "Phrase"),
        ('"composition opportunities 2027"', "Phrase"),
        ('"where to submit my score"', "Phrase"),
        ('"submit score to ensemble"', "Phrase"),
     ], SITE + "/opportunities.html"),

    ("CB | Calls for Scores | American", "American composers", [
        ('"call for scores american composers"', "Phrase"),
        ('"opportunities for american composers"', "Phrase"),
        ('"chamber music call for scores usa"', "Phrase"),
        ('[american composers call for scores]', "Exact"),
     ], SITE + "/calls/scores-american.html"),

    ("CB | Calls for Scores | American", "US composition calls", [
        ('"composition competitions united states"', "Phrase"),
        ('"new music opportunities usa"', "Phrase"),
        ('"us composers submit chamber work"', "Phrase"),
     ], SITE + "/calls/scores-american.html"),

    ("CB | Brand", "CreArtBox", [
        ('"creartbox"', "Phrase"),
        ('[creartbox]', "Exact"),
        ('"creartbox nyc"', "Phrase"),
        ('"creartbox ensemble"', "Phrase"),
        ('"creartbox new york"', "Phrase"),
     ], SITE + "/"),

    ("CB | Brand", "Festival ADAR", [
        ('"festival adar"', "Phrase"),
        ('"festival adar asturias"', "Phrase"),
     ], SITE + "/projects.html"),
]

# Evergreen. Nothing here names a date, a programme or a price, so it
# does not go stale between concerts.
CONCERT_HEADLINES = [
    "Chamber Music in New York", "Live at The DiMenna Center",
    "Classical Concerts in NYC", "New Music Beside Brahms",
    "CreArtBox New York Series", "Midtown Manhattan, 7:30 pm",
    "Quintet, Quartet and Trio", "A New York Ensemble, 2013",
    "450 West 37th Street", "Video Art and Live Music",
    "Four Productions a Season", "See the Season Calendar",
    "An Hour of Chamber Music", "Standard and New Work",
    "Tickets Through Eventbrite",
]
CONCERT_DESCRIPTIONS = [
    "Four productions a season at The DiMenna Center, Midtown Manhattan, each at 7:30 pm.",
    "A New York ensemble since 2013. Standard repertoire and new work in one evening.",
    "The hall, the start time, the running time and what a seat costs, before you come.",
    "See every date of the season, in New York and on tour. Tickets through Eventbrite.",
]

# For the concert on sale. REWRITE THIS AFTER EVERY CONCERT: the date,
# the composers and the price are the ones on the ticket page, and the
# ad is wrong the morning after. Currents, 30 October 2026, $15 and up.
DATED_HEADLINES = [
    "Brahms and Both Schumanns", "Tickets from $15",
    "Friday 30 October, 7:30 pm", "Currents at The DiMenna",
    "Chamber Music in New York", "An Hour, No Intermission",
    "Clara Schumann, Op. 22", "Schumann Piano Quartet",
    "Live at The DiMenna Center", "Midtown Manhattan, 7:30 pm",
    "Video Art and Live Music", "CreArtBox New York Series",
    "450 West 37th Street", "Quintet, Quartet and Trio",
    "A New York Ensemble, 2013",
]
DATED_DESCRIPTIONS = [
    "Brahms, Clara and Robert Schumann with two contemporary works. Tickets from $15.",
    "An hour of chamber music at The DiMenna Center, Midtown Manhattan. No intermission.",
    "Friday 30 October 2026, 7:30 pm, 450 West 37th Street. A New York ensemble since 2013.",
    "Five works for two to four players, with video art. Tickets through Eventbrite.",
]

CALL_HEADLINES = [
    "Call for Scores 2027/28", "Open to Any Instrumentation",
    "Deadline 15 December 2026", "First Round Read Blind",
    "For Composers Worldwide", "American Composers Welcome",
    "Played in New York", "Two Works, $20 to Apply",
    "Any Age, Any Career Stage", "CreArtBox Call for Scores",
    "Your Score Beside Brahms", "Performed and Recorded",
    "Players and Composers Read", "An Answer by Spring 2027",
    "One Form, Two Scores",
]
CALL_DESCRIPTIONS = [
    "Two works, any instrumentation, any career stage. Deadline 15 December 2026.",
    "The first round is read blind. Selected works are played in the 2027/28 season.",
    "Eleven works in the current season arrived through this call. $20 to apply.",
    "Read by the five musicians who would play it, and by composers chosen before.",
]

BRAND_HEADLINES = [
    "CreArtBox", "CreArtBox, New York", "Chamber Music Ensemble",
    "Concerts, Calls and Archive", "New York Series and Tour",
    "Founded in New York, 2013", "A 501(c)(3) Non-Profit",
    "The DiMenna Center Series", "Festival ADAR, Asturias",
    "Every Concert Since 2013",
]
BRAND_DESCRIPTIONS = [
    "A New York chamber music ensemble founded in 2013. Concerts, calls and archive.",
    "The New York Series at The DiMenna Center, touring dates and Festival ADAR.",
    "Twelve seasons of chamber music, with new work in every programme.",
    "See the calendar, the repertoire and the open calls for composers.",
]

# keyed by ad group where the copy is specific to one, by campaign otherwise
COPY = {
    ("CB | Concerts | New York", "Currents, 30 October"):
        (DATED_HEADLINES, DATED_DESCRIPTIONS, "concerts", "currents"),
    "CB | Concerts | New York": (CONCERT_HEADLINES, CONCERT_DESCRIPTIONS, "concerts", "new-york"),
    "CB | Calls for Scores | International": (CALL_HEADLINES, CALL_DESCRIPTIONS, "call-for-scores", "2027-28"),
    "CB | Calls for Scores | American": (CALL_HEADLINES, CALL_DESCRIPTIONS, "call-for-scores", "american"),
    "CB | Brand": (BRAND_HEADLINES, BRAND_DESCRIPTIONS, "about", ""),
}

SITELINKS = [
    ("Season calendar", "Every date of the twelfth season", "Four New York productions",
     SITE + "/concerts.html"),
    ("Coming to a concert", "The hall, the way in, the price", "Start and running times",
     SITE + "/classical-concerts-nyc.html"),
    ("Open calls", "Two calls for scores are open", "Deadline 15 December 2026",
     SITE + "/opportunities.html"),
    ("About the ensemble", "A New York ensemble since 2013", "Biographies and press kit",
     SITE + "/about.html"),
]


def check(kind, text):
    limit = LIMITS[kind]
    if len(text) > limit:
        raise SystemExit("TOO LONG (%d > %d) %s: %r" % (len(text), limit, kind, text))
    return text


def write(name, header, rows):
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print("wrote %-22s %d row(s)" % (name, len(rows)))


def main():
    for h in CONCERT_HEADLINES + DATED_HEADLINES + CALL_HEADLINES + BRAND_HEADLINES:
        check("headline", h)
    for d in (CONCERT_DESCRIPTIONS + DATED_DESCRIPTIONS + CALL_DESCRIPTIONS
              + BRAND_DESCRIPTIONS):
        check("description", d)
    for text, d1, d2, _ in SITELINKS:
        check("sitelink", text)
        check("sitelink_desc", d1)
        check("sitelink_desc", d2)

    write("1-campaigns.csv",
          ["Campaign", "Campaign Daily Budget", "Campaign Type", "Networks",
           "Bid Strategy Type", "Locations", "Languages", "Campaign Status"],
          [[c["name"], c["budget"], "Search", "Google search",
            "Maximize conversions", c["locations"], "English", "Paused"]
           for c in CAMPAIGNS])

    write("2-ad-groups.csv",
          ["Campaign", "Ad Group", "Max CPC", "Ad Group Status"],
          [[camp, group, "2.00", "Enabled"] for camp, group, _, _ in AD_GROUPS])

    # The policy forbids single-word keywords except for its own listed
    # exceptions, of which a nonprofit's own brand name is one.
    brand_words = {"creartbox", "creartbox.nyc"}
    rows = []
    for camp, group, keywords, url in AD_GROUPS:
        for kw, match in keywords:
            bare = kw.strip('"[]').lower()
            if len(bare.split()) < 2 and bare not in brand_words:
                raise SystemExit("single-word keyword, which the policy forbids: " + kw)
            rows.append([camp, group, kw, match, "Enabled", url])
    write("3-keywords.csv",
          ["Campaign", "Ad Group", "Keyword", "Match Type", "Status", "Final URL"], rows)

    rows = []
    for camp, group, _, url in AD_GROUPS:
        heads, descs, p1, p2 = COPY.get((camp, group)) or COPY[camp]
        row = [camp, group, "Responsive search ad", url,
               check("path", p1), check("path", p2) if p2 else ""]
        row += list(heads[:15]) + [""] * (15 - len(heads[:15]))
        row += list(descs[:4]) + [""] * (4 - len(descs[:4]))
        row.append("Enabled")
        rows.append(row)
    write("4-ads.csv",
          ["Campaign", "Ad Group", "Ad Type", "Final URL", "Path 1", "Path 2"]
          + ["Headline %d" % i for i in range(1, 16)]
          + ["Description %d" % i for i in range(1, 5)] + ["Status"], rows)

    write("5-sitelinks.csv",
          ["Campaign", "Sitelink Text", "Description Line 1", "Description Line 2",
           "Final URL"],
          [[c["name"], t, d1, d2, u] for c in CAMPAIGNS for t, d1, d2, u in SITELINKS])

    print("\nevery headline, description and sitelink is inside Google's limits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
