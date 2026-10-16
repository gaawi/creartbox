#!/usr/bin/env python3
"""Move a concert that has happened into the archive.

    python3 tools/archive_past.py            # move everything past
    python3 tools/archive_past.py --check    # fail if something is overdue

A date in the calendar that has passed is still sitting on the site as
if tickets were coming, so once it is over it moves: the concert page
becomes an archive page, an entry goes into the year on archive.html,
and the row leaves concerts.html. Links elsewhere on the site that
pointed at the old page are rewritten to the archive one.

The dates come from the calendar rows themselves, which carry the day,
the month and the year, and "to Oct 9" when a date runs over several
days. Nothing is invented here: every field of the archive entry is
already in the row or on the concert page.
"""

import datetime
import glob
import os
import re
import sys

TODAY = datetime.date.today()
MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

ROW_RE = re.compile(r'\n *<tr [^>]*>.*?</tr>\n', re.S)
WHEN_RE = re.compile(r'<td class="when">(.*?)</td>', re.S)
HREF_RE = re.compile(r'<div class="title-cell"><a href="concerts/([^"]+)\.html">(.*?)</a>')
LABEL_RE = re.compile(r'<div class="label"[^>]*>(.*?)</div>', re.S)
WHERE_RE = re.compile(r'<td class="where">(.*?)<br><span[^>]*>(.*?)</span></td>', re.S)


def text(fragment):
    return re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", fragment)).strip()


def parse_row(row):
    """What the archive needs, read off the calendar row."""
    href = HREF_RE.search(row)
    when = WHEN_RE.search(row)
    if not href or not when:
        return None
    cell = when.group(1)
    day = re.search(r'<span class="num">(\d+)</span>', cell)
    month_year = re.search(r">([A-Z][a-z]{2}) (\d{4})<", cell)
    if not day or not month_year:
        return None
    month, year = month_year.group(1), int(month_year.group(2))
    start = datetime.date(year, MONTHS[month], int(day.group(1)))

    # "to Oct 9" on a date that runs over several days
    end = start
    span = re.search(r">to ([A-Z][a-z]{2}) (\d+)<", cell)
    days = day.group(1)
    if span:
        end = datetime.date(year, MONTHS[span.group(1)], int(span.group(2)))
        days = "%s-%s" % (day.group(1), span.group(2))

    where = WHERE_RE.search(row)
    label = LABEL_RE.search(row)
    return {
        "row": row,
        "slug": href.group(1),
        "title": text(href.group(2)),
        "part_of": text(label.group(1)) if label else "",
        "venue": text(where.group(1)) if where else "",
        "place": text(where.group(2)) if where else "",
        "start": start, "end": end,
        "year": year, "month": month, "days": days,
        "archive": "%s-%d-%02d" % (href.group(1), year, MONTHS[month]),
    }


def past_rows(src):
    rows = [parse_row(m.group(0)) for m in ROW_RE.finditer(src)]
    return [r for r in rows if r and r["end"] < TODAY]


# ------------------------------------------------------------ the page

def archive_page(event):
    """The concert page, rewritten as a record of something that happened."""
    src = open("concerts/%s.html" % event["slug"], encoding="utf-8").read()

    src = src.replace('<section class="event-page concert-landing">',
                      '<section class="event-page">')
    src = src.replace(
        '<a href="../concerts.html" class="back-to-archive">&#8592; All upcoming concerts</a>',
        '<a href="../archive.html" class="back-to-archive">&#8592; Archive of performances</a>')
    src = src.replace(
        '<a href="../concerts.html" class="back-to-archive">← All upcoming concerts</a>',
        '<a href="../archive.html" class="back-to-archive">← Archive of performances</a>')
    src = src.replace('<div class="event-series">%s</div>' % event["part_of"],
                      '<div class="event-series">Part of: %s</div>' % event["part_of"])
    src = src.replace('<div class="meta-h">When</div>', '<div class="meta-h">Date</div>')
    src = src.replace('<div class="meta-h">Series</div>', '<div class="meta-h">Part of</div>')
    # tickets are over
    src = re.sub(r'\n *<div class="ticket-cta">.*?</div>\n *</div>\n', "\n", src, flags=re.S)
    src = re.sub(r'<a href="\.\./concerts\.html" class="btn">(&#8592;|←) All upcoming concerts</a>',
                 '<a href="../archive.html" class="btn">&#8592; Archive of performances</a>', src)
    # the head: it is an archive page now
    src = src.replace('<link rel="canonical" href="https://creartbox.nyc/concerts/%s.html">'
                      % event["slug"],
                      '<link rel="canonical" href="https://creartbox.nyc/archive/%s.html">'
                      % event["archive"])
    src = src.replace('<div class="nav-item"><a href="../concerts.html" class="active">Calendar</a></div>',
                      '<div class="nav-item"><a href="../concerts.html">Calendar</a></div>')
    src = src.replace('<div class="nav-item"><a href="../archive.html">Archive</a></div>',
                      '<div class="nav-item"><a href="../archive.html" class="active">Archive</a></div>')
    return src


ENTRY = """		<div class="eventpast nophoto">
			<div class="calendardatepast">
				<span class="yearpast">{year}</span><span class="monthpast">{month}</span><span class="daypast">{days}</span>
			</div>
			<h3>
				{title}
			</h3>
			<h5 class="partofpast">
				<strong>Part of:</strong> {part_of}
			</h5>
			<h5 class="address">
				<i aria-hidden="true" class="fa fa-map-marker"></i>{place}
			</h5>
			<div class="explore">
				<a class="button" href="archive/{archive}.html">View more</a>
			</div>
		</div>
"""


def add_entry(src, event):
    """Newest first inside its year, which is where the year block starts."""
    head = re.search(r'id="y%d"[^>]*>\s*\n\s*%d\s*\n\s*</h1>\s*\n\s*<div class="calendarpast"[^>]*>\n'
                     % (event["year"], event["year"]), src)
    if not head:
        sys.exit("  !! no %d block in archive.html" % event["year"])
    at = head.end()
    return src[:at] + ENTRY.format(**event) + src[at:]


def relink(event):
    """Pages that pointed at the concert now point at the record of it."""
    touched = []
    for path in (sorted(glob.glob("*.html")) + sorted(glob.glob("*/*.html"))
                 + sorted(glob.glob("news/_posts/*.md"))):
        if path.startswith("archive/"):
            continue
        src = open(path, encoding="utf-8").read()
        depth = "../" if "/" in path else ""
        out = src.replace('%sconcerts/%s.html' % (depth, event["slug"]),
                          '%sarchive/%s.html' % (depth, event["archive"]))
        if path.startswith("news/_posts/"):
            out = src.replace("concerts/%s.html" % event["slug"],
                              "archive/%s.html" % event["archive"])
        if out != src:
            open(path, "w", encoding="utf-8").write(out)
            touched.append(path)
    return touched


def main():
    check = "--check" in sys.argv
    calendar = open("concerts.html", encoding="utf-8").read()
    events = past_rows(calendar)

    if check:
        if events:
            print("%d date(s) have passed and are still in the calendar:" % len(events))
            for e in events:
                print("  - %s, %s %s %d" % (e["title"], e["month"], e["days"], e["year"]))
            print("\nRun: python3 tools/archive_past.py")
            return 1
        print("the calendar holds nothing that has already happened")
        return 0

    if not events:
        print("nothing to archive")
        return 0

    archive = open("archive.html", encoding="utf-8").read()
    for event in sorted(events, key=lambda e: e["start"]):
        page = "archive/%s.html" % event["archive"]
        open(page, "w", encoding="utf-8").write(archive_page(event))
        archive = add_entry(archive, event)
        calendar = calendar.replace(event["row"], "\n")
        os.remove("concerts/%s.html" % event["slug"])
        moved = relink(event)
        print("%s -> %s%s" % (event["slug"], page,
                              ("   relinked: " + ", ".join(moved)) if moved else ""))

    open("archive.html", "w", encoding="utf-8").write(archive)
    open("concerts.html", "w", encoding="utf-8").write(calendar)
    print("\nNow run: python3 tools/sync_next_event.py && python3 tools/link_performer_bios.py"
          " && python3 tools/build_news.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
