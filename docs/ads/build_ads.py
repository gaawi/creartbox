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

THE LIVE ACCOUNT IS NOW AHEAD OF THIS FILE. The account was built on
9 November 2026 from these files, and whoever built it rewrote five
headlines that the site did not support. Those five are fixed here too,
checked again against the site:

    "Ma Mere l'Oye, Four Hands"  the page lists one pianist
    "Quintet, Quartet and Trio"  no quartet in the programme
    "An Hour of Chamber Music"   Winterlight runs about 80 minutes
    "New Music Beside Brahms"    Brahms was in Currents, which has gone
    "Your Score Beside Brahms"   the same
    worldwide vs American        the two calls were sharing one line

The last of those was the worst of them: the two calls have different
eligibility, so an ad that said both was wrong on one of the two pages.
They now have their own headline and their own first description.

The exact wording live in the account may still differ from what this
file writes. Reconcile from the account's own export before importing
again, or an import will overwrite an ad somebody improved on screen.
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://creartbox.nyc"

# Google's limits for a responsive search ad and its assets
LIMITS = {"headline": 30, "description": 90, "path": 15,
          "sitelink": 25, "sitelink_desc": 35,
          "callout": 25, "snippet": 25}

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
    # Shorter keywords, after the account reported Low search volume on 14
    # of 21 concert keywords and 6 of 7 American ones. A six-word phrase
    # describes the evening exactly and is typed by nobody. The long tail
    # is kept where it is plausible; the short head is what will serve.
    #
    # None is a single word, and none is the kind of bare generic the
    # policy forbids. "chamber music nyc" is the shape Google's own
    # example allows: "museums in [your city name]".
    ("CB | Concerts | New York", "Chamber music NYC", [
        ('"chamber music nyc"', "Phrase"),
        ('[chamber music nyc]', "Exact"),
        ('"chamber music new york"', "Phrase"),
        ('"chamber music concert"', "Phrase"),
        ('"chamber music concerts new york"', "Phrase"),
        ('"chamber music nyc tickets"', "Phrase"),
     ], SITE + "/classical-concerts-nyc.html"),

    ("CB | Concerts | New York", "Classical concerts NYC", [
        ('"classical concerts nyc"', "Phrase"),
        ('[classical concerts nyc]', "Exact"),
        ('"classical music nyc"', "Phrase"),
        ('"classical concert new york"', "Phrase"),
        ('"live classical music nyc"', "Phrase"),
        ('"classical music concerts new york city"', "Phrase"),
     ], SITE + "/classical-concerts-nyc.html"),

    ("CB | Concerts | New York", "DiMenna Center", [
        ('"dimenna center"', "Phrase"),
        ('[dimenna center]', "Exact"),
        ('"dimenna center concerts"', "Phrase"),
        ('"dimenna center for classical music"', "Phrase"),
     ], SITE + "/classical-concerts-nyc.html"),

    # 6 of these 7 came back Low search volume. One concert, in one city,
    # on one night is not a thing people search for by name until they
    # have heard of it. The volume lives in the three ad groups above.
    ("CB | Concerts | New York", "Winterlight, 11 December", [
        ('"stravinsky petrushka"', "Phrase"),
        ('"petrushka concert"', "Phrase"),
        ('"stravinsky concert nyc"', "Phrase"),
        ('"ravel ma mere loye"', "Phrase"),
        ('"stravinsky petrushka new york"', "Phrase"),
        ('"petroushka new york"', "Phrase"),
        ('"ma mere loye concert"', "Phrase"),
     ], SITE + "/concerts/winterlight-2026.html"),

    # Ten pairs of tickets given away for Winterlight. This is the only
    # ad group in the account whose landing page costs the reader
    # nothing, and "free concert tickets nyc" is typed far more than any
    # composer's name, so it is likely to carry the campaign. It lives
    # until the draw on 4 December and is paused the morning after.
    ("CB | Concerts | New York", "Ticket lottery", [
        ('"free concert tickets nyc"', "Phrase"),
        ('"free tickets nyc"', "Phrase"),
        ('"free concert new york"', "Phrase"),
        ('"free classical concert nyc"', "Phrase"),
        ('"win concert tickets nyc"', "Phrase"),
        ('"ticket lottery nyc"', "Phrase"),
        ('[free concert tickets nyc]', "Exact"),
     ], SITE + "/lottery.html"),

    ("CB | Calls for Scores | International", "Call for scores", [
        ('"call for scores"', "Phrase"),
        ('[call for scores]', "Exact"),
        ('"call for scores 2027"', "Phrase"),
        ('"open call for scores"', "Phrase"),
        ('"composer call for scores"', "Phrase"),
        ('"call for scores chamber music"', "Phrase"),
     ], SITE + "/calls/scores-international.html"),

    ("CB | Calls for Scores | International", "Composer opportunities", [
        ('"composer opportunities"', "Phrase"),
        ('"composition opportunities"', "Phrase"),
        ('"opportunities for composers"', "Phrase"),
        ('"new music opportunities"', "Phrase"),
        ('"submit score to ensemble"', "Phrase"),
     ], SITE + "/opportunities.html"),

    # Nearly every keyword here came back Low search volume, and the
    # reason is structural rather than fixable: a composer looking for a
    # call types "call for scores", not "call for scores for American
    # composers". See the note in RUNBOOK-launch.md on merging the two
    # calls campaigns.
    ("CB | Calls for Scores | American", "American composers", [
        ('"call for scores american"', "Phrase"),
        ('"american composer opportunities"', "Phrase"),
        ('"call for scores american composers"', "Phrase"),
        ('"opportunities for american composers"', "Phrase"),
     ], SITE + "/calls/scores-american.html"),

    ("CB | Calls for Scores | American", "US composition calls", [
        ('"composition competition"', "Phrase"),
        ('"music composition competition"', "Phrase"),
        ('"new music competition"', "Phrase"),
        ('"composition competitions united states"', "Phrase"),
     ], SITE + "/calls/scores-american.html"),

    # 3 of 7 Low search volume, which is what a brand campaign for a
    # chamber ensemble looks like and is not a problem to solve. It is
    # here to defend the name and to hold up the account click-through
    # rate, not to find volume.
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
    "Classical Concerts in NYC", "Premieres and Classics",
    "CreArtBox New York Series", "Midtown Manhattan, 7:30 pm",
    "Flute, Piano and Strings", "A New York Ensemble, 2013",
    "450 West 37th Street", "Video Art and Live Music",
    "Four Productions a Season", "See the Season Calendar",
    "A, C and E to Penn Station", "Standard and New Work",
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
# ad is wrong the morning after. Winterlight, 11 December 2026, $15 to
# $70, read from the Eventbrite listing on 31 October 2026.
DATED_HEADLINES = [
    "Stravinsky and Ravel", "Tickets from $15",
    "Friday 11 December, 7:30pm", "Winterlight at The DiMenna",
    "Petroushka in New York", "A World Premiere, Dec 11",
    "Chamber Music in New York", "Live Visual Projections",
    "Midtown Manhattan, 7:30 pm", "CreArtBox New York Series",
    "450 West 37th Street", "Ravel's Ma Mere l'Oye",
    "Flute, Piano and Strings", "A New York Ensemble, 2013",
    "Stravinsky's Petroushka",
]
DATED_DESCRIPTIONS = [
    "Stravinsky's Petroushka and Ravel's Ma Mere l'Oye with visual projections. From $15.",
    "Friday 11 December 2026, 7:30 pm at The DiMenna Center, Midtown Manhattan.",
    "A world premiere by Hannah Selin, and a work chosen through the open call.",
    "Chamber music with projections made for the programme. Tickets through Eventbrite.",
]

# The two calls have different eligibility and must not share the line
# that states it. The international call is open to composers "of any
# nationality"; the American one asks for United States citizenship, or
# residence in the United States or its territories for a significant
# period. One ad saying both would be wrong on one of the two pages.
LOTTERY_HEADLINES = [
    "Ten Pairs of Tickets, Free", "Free Tickets to Winterlight",
    "Win Two Tickets in New York", "A Ticket Lottery, Dec 11",
    "Enter by December 3", "Free Chamber Music Tickets",
    "Ten Winners, Two Seats Each", "One Email, One Sentence",
    "No Purchase, No Sign-Up", "The DiMenna Center, NYC",
    "Stravinsky and Ravel", "Friday 11 December, 7:30pm",
    "Everyone Hears the Result", "Draw on December 4",
    "Midtown Manhattan, 7:30 pm",
]
LOTTERY_DESCRIPTIONS = [
    "Ten pairs of tickets to Winterlight, free. Email one sentence on why you would come.",
    "Entries close 3 December. The draw is 4 December and everyone who entered hears back.",
    "Nothing to buy and nothing to sign up for. One email, subject WINTERLIGHT LOTTERY.",
    "Stravinsky and Ravel at The DiMenna Center, Friday 11 December, 7:30 pm.",
]

CALL_HEADLINES = [
    "Call for Scores 2027/28", "Open to Any Instrumentation",
    "Deadline 15 December 2026", "First Round Read Blind",
    "Played in New York", "Two Works, $20 to Apply",
    "Any Age, Any Career Stage", "CreArtBox Call for Scores",
    "Eleven Works This Season", "Performed and Recorded",
    "Players and Composers Read", "An Answer by Spring 2027",
]
INTL_HEADLINES = CALL_HEADLINES + [
    "Composers of Any Nationality", "For the 2027/28 Season",
    "One Form, Two Scores",
]
AMER_HEADLINES = CALL_HEADLINES + [
    "For American Composers", "US Citizens and Residents",
    "One Form, Two Scores",
]
CALL_DESCRIPTIONS = [
    "The first round is read blind. Selected works are played in the 2027/28 season.",
    "Eleven works in the current season arrived through this call. $20 to apply.",
    "Read by the five musicians who would play it, and by composers chosen before.",
]
# again, the eligibility line differs
INTL_DESCRIPTIONS = [
    "Any nationality, any instrumentation, any career stage. Deadline 15 December 2026.",
] + CALL_DESCRIPTIONS
AMER_DESCRIPTIONS = [
    "For American composers. Two works, any instrumentation. Deadline 15 December 2026.",
] + CALL_DESCRIPTIONS

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
    ("CB | Concerts | New York", "Winterlight, 11 December"):
        (DATED_HEADLINES, DATED_DESCRIPTIONS, "concerts", "winterlight"),
    ("CB | Concerts | New York", "Ticket lottery"):
        (LOTTERY_HEADLINES, LOTTERY_DESCRIPTIONS, "free", "tickets"),
    "CB | Concerts | New York": (CONCERT_HEADLINES, CONCERT_DESCRIPTIONS, "concerts", "new-york"),
    "CB | Calls for Scores | International": (INTL_HEADLINES, INTL_DESCRIPTIONS, "call-for-scores", "2027-28"),
    "CB | Calls for Scores | American": (AMER_HEADLINES, AMER_DESCRIPTIONS, "call-for-scores", "american"),
    "CB | Brand": (BRAND_HEADLINES, BRAND_DESCRIPTIONS, "about", ""),
}

# Negative keywords, which are most of what keeps the account-wide
# click-through rate above the 5% Google requires. Each list says which
# campaigns it applies to. Broad by default, because a negative is meant
# to catch a whole family of queries; phrase where the bare word is too
# common to block outright.
#
#   NEVER  ... everything. Free files, jobs, lessons, reference lookups,
#              private hire, bargain hunting. Note that the bare word
#              "free" is NOT in it. It was, and it would have blocked
#              every keyword for the ticket lottery, which is free and
#              is the one thing in this account that can honestly say
#              so. The free-something phrases below do the same job
#              without taking the word away.
#   VENUE  ... the concerts campaign. The DiMenna Center's own main
#              business is renting rehearsal and recording rooms, so most
#              of the search volume on its name is musicians looking to
#              book one, not an audience looking for a ticket. Also other
#              halls, and other genres.
#   SCORES ... the calls campaigns. The word "score" belongs to sport and
#              to standardised tests far more than it belongs to music,
#              and this call charges a fee and awards no prize money.
#   BRAND  ... the brand campaign. Adar is also a month in the Hebrew
#              calendar, and Festival ADAR is not.
NEGATIVE_LISTS = [
    ("CB | Never", [c["name"] for c in CAMPAIGNS], """
        download, downloads, mp3, pdf, torrent, streaming, youtube,
        lyrics, karaoke, imslp, sheet music, score pdf, piano reduction,
        backing track,

        free download, free mp3, free sheet music, free streaming,
        watch free, listen free, free online, free pdf,

        job, jobs, hiring, salary, vacancy, internship, employment,
        audition, auditions, resume, cv,

        lessons, teacher, tutor, course, courses, masterclass, degree,
        school, conservatory, university, syllabus, tutorial, exam,
        grade, how to play,

        wikipedia, meaning, analysis, definition, biography, who wrote,
        who composed, history of,

        wedding, weddings, funeral, dj, cover band, background music,
        buy violin, violin for sale, instrument rental, rent a piano,

        cheap, coupon, refund, discount code, promo code
    """),

    ("CB | Not an audience", ["CB | Concerts | New York"], """
        rehearsal, rehearsal space, studio, studios, recording studio,
        practice room, book a room, rent, rental, booking, hourly,
        rates, parking,

        carnegie hall, lincoln center, metropolitan opera,
        new york philharmonic, david geffen, 92nd street y,
        kaufman music center, le poisson rouge, merkin, juilliard,
        mannes, bargemusic,

        opera, ballet, jazz, rock, pop, musical, broadway, choir,
        chorus, gospel, country, hip hop
    """),

    ("CB | Not a composer", ["CB | Calls for Scores | International",
                             "CB | Calls for Scores | American"], """
        football, nfl, nba, soccer, cricket, baseball, hockey, fico,
        gpa, live score, final score, credit score, sat scores,
        act scores, test score, exam score,

        scholarship, funding, no fee, no entry fee, without fee,
        fee waiver, cash prize, prize money, grants for composers,
        commission fee,

        film scoring, video game music, library music, production music,
        sync licensing, beat making, jingle
    """),

    ("CB | Brand noise", ["CB | Brand"], """
        login, log in, sign in, app, careers, complaints, scam,
        purim, torah, jewish calendar, rosh chodesh, adar sheni,
        hebrew month
    """),
]


def parse_negatives(spec):
    """Read a negative block into (term, match type) pairs.

    A single word blocks every query containing it, so it goes in broad.
    Anything of two words or more only makes sense as a phrase: blocking
    "sheet" and "music" separately would take out half the account.
    """
    out = []
    for raw in spec.split(","):
        term = " ".join(raw.split())
        if not term:
            continue
        out.append((term, "Negative Broad" if " " not in term
                    else "Negative Phrase"))
    return out


# Headlines that belong to one ad group and name what that ad group is
# about. Ad Strength came back Poor on five ads, and the usual reason is
# an ad whose headlines never contain the keyword that triggered it: four
# ad groups were sharing one set of copy. These go first, so every ad
# leads with its own subject.
EXTRA = {
    ("CB | Concerts | New York", "Chamber music NYC"): [
        "Chamber Music in NYC", "Chamber Music, Midtown",
        "A Chamber Music Evening", "Chamber Music Tickets",
    ],
    ("CB | Concerts | New York", "Classical concerts NYC"): [
        "Classical Concerts in NYC", "Live Classical in Midtown",
        "A Classical Concert, NYC", "Classical Music Tickets",
    ],
    ("CB | Concerts | New York", "DiMenna Center"): [
        "Live at The DiMenna Center", "Concerts at The DiMenna",
        "The DiMenna Center, NYC", "450 West 37th Street",
    ],
    ("CB | Concerts | New York", "Ticket lottery"): [
        "Free Concert Tickets, NYC", "A Free Ticket to Winterlight",
        "Ten Pairs, Given Away", "Free Tickets, December 11",
    ],
    ("CB | Calls for Scores | International"
     , "Call for scores"): [
        "An Open Call for Scores", "Call for Scores 2027/28",
        "Send Two Scores", "Scores Read Blind",
    ],
    ("CB | Calls for Scores | International", "Composer opportunities"): [
        "Opportunities for Composers", "For Composers, Any Stage",
        "Where to Send a Score", "An Open Call, Dec 15",
    ],
    ("CB | Calls for Scores | American", "American composers"): [
        "For American Composers", "American Composers, Apply",
        "A Call for US Composers", "US Composers, Played in NY",
    ],
    ("CB | Calls for Scores | American", "US composition calls"): [
        "A Composition Call, US", "Open to US Composers",
        "New Music, Played Live", "Composers: Deadline Dec 15",
    ],
}

# Callouts are 25 characters and are not clickable, so every one has to
# be a fact worth reading on its own. All of these are on the site.
CALLOUTS = {
    "CB | Concerts | New York": [
        "Midtown Manhattan", "Tickets from $15",
        "Concerts start 7:30 pm", "A 501(c)(3) non-profit",
    ],
    "CB | Calls for Scores | International": [
        "$20 to apply", "Two works per entry",
        "Any instrumentation", "First round read blind",
    ],
    "CB | Calls for Scores | American": [
        "$20 to apply", "Two works per entry",
        "Any instrumentation", "First round read blind",
    ],
    "CB | Brand": [
        "A 501(c)(3) non-profit", "New York since 2013",
        "Four productions a season", "Festival ADAR, Asturias",
    ],
}

# One structured snippet per campaign. The header has to come from
# Google's fixed list; "Styles" is the one that fits music.
SNIPPETS = {
    "CB | Concerts | New York":
        ("Styles", ["Chamber music", "Classical", "Contemporary", "New music"]),
    "CB | Calls for Scores | International":
        ("Styles", ["Chamber music", "Contemporary", "New music", "Any instrumentation"]),
    "CB | Calls for Scores | American":
        ("Styles", ["Chamber music", "Contemporary", "New music", "Any instrumentation"]),
    "CB | Brand":
        ("Styles", ["Chamber music", "Classical", "Contemporary", "Video art"]),
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
    ("Free tickets", "Ten pairs given away", "Enter by 3 December",
     SITE + "/lottery.html"),
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
    for h in (CONCERT_HEADLINES + DATED_HEADLINES + LOTTERY_HEADLINES
              + INTL_HEADLINES
              + AMER_HEADLINES + BRAND_HEADLINES):
        check("headline", h)
    for d in (CONCERT_DESCRIPTIONS + DATED_DESCRIPTIONS + LOTTERY_DESCRIPTIONS
              + INTL_DESCRIPTIONS
              + AMER_DESCRIPTIONS
              + BRAND_DESCRIPTIONS):
        check("description", d)
    for group in EXTRA.values():
        for h in group:
            check("headline", h)
    for group in CALLOUTS.values():
        for c in group:
            check("callout", c)
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
        own = [h for h in EXTRA.get((camp, group), []) if h not in heads]
        heads = own + list(heads)
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

    # Negatives, twice over: once as a campaign-level import for Google
    # Ads Editor, and once as plain text, because the web interface takes
    # a pasted list and that is the quicker route to a shared list.
    rows, listing, total = [], [], 0
    for name, campaigns, spec in NEGATIVE_LISTS:
        terms = parse_negatives(spec)
        total += len(terms)
        listing.append("# %s\n# applies to: %s\n%s\n"
                       % (name, ", ".join(campaigns),
                          "\n".join(t for t, _ in terms)))
        for camp in campaigns:
            rows += [[camp, term, match] for term, match in terms]
    write("6-negatives.csv", ["Campaign", "Keyword", "Criterion Type"], rows)

    path = os.path.join(HERE, "6-negatives.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(listing))
    print("wrote %-22s %d term(s) in %d list(s)"
          % ("6-negatives.txt", total, len(NEGATIVE_LISTS)))

    write("7-callouts.csv", ["Campaign", "Callout text"],
          [[camp, text] for camp, texts in CALLOUTS.items() for text in texts])

    rows = []
    for camp, (header, values) in SNIPPETS.items():
        for v in values:
            check("snippet", v)
        rows.append([camp, header, "; ".join(values)])
    write("8-snippets.csv", ["Campaign", "Header", "Values"], rows)

    print("\nevery headline, description, sitelink and callout "
          "is inside Google's limits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
