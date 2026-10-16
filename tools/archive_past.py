#!/usr/bin/env python3
"""Move a concert that has happened into the archive.

    python3 tools/archive_past.py            # move everything past
    python3 tools/archive_past.py --check    # fail if something is overdue

A date in the calendar that has passed is still sitting on the site as
if tickets were coming, so once it is over it moves: an entry goes into
its year on archive.html, carrying the date, the title, what it was part
of, the place, the photograph and the programme behind a "View Program"
button, and the row and the concert page go. The archive is one page:
nothing here writes a page of its own. Links elsewhere on the site that
pointed at the concert are rewritten to its year in the archive.

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


PROGRAM_RE = re.compile(
    r'<li[^>]*><span class="rp-composer">(.*?)</span><span class="rp-work">(.*?)</span></li>', re.S)
MANUAL_RE = re.compile(r'<ul data-program-manual[^>]*>(.*?)</ul>', re.S)
HERO_RE = re.compile(r'<figure class="concert-hero"><img src="\.\./([^"]+)"')


def program_of(row):
    """[(composer, work), ...] as the calendar row lists them."""
    works = [(text(c), text(w)) for c, w in PROGRAM_RE.findall(row)]
    if works:
        return works
    manual = MANUAL_RE.search(row)
    if manual:
        return [("", text(li)) for li in re.findall(r"<li[^>]*>(.*?)</li>", manual.group(1), re.S)]
    return []


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
        "program": program_of(row),
    }


def past_rows(src):
    rows = [parse_row(m.group(0)) for m in ROW_RE.finditer(src)]
    return [r for r in rows if r and r["end"] < TODAY]


# ----------------------------------------------------------- the entry

MODAL = """<button class="myBtn_multi">View Program</button>
			<div class="modal modal_multi">
				<div class="modal-content">
					<span class="close close_multi">&#215;</span>
{works}				</div>
			</div>
"""

# with a photograph the text sits in a div of its own beside it, which is
# what the grid in the stylesheet expects
ENTRY = """		<div class="eventpast{bare}">
{photo}{open_text}			<div class="calendardatepast">
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
			</h5>{program}{close_text}		</div>
"""

PHOTO = ('\t\t\t<img class="imgpastevents" height="inherit" src="{src}" '
         'width="auto" loading="lazy">\n')


def entry(event):
    """The record of one date, inside the archive page itself."""
    works = ""
    for composer, work in event["program"]:
        if composer:
            works += "\t\t\t\t\t<strong>%s</strong><br>\n" % composer
        works += "\t\t\t\t\t%s<br>\n" % work
    hero = HERO_RE.search(open("concerts/%s.html" % event["slug"], encoding="utf-8").read())
    # the photo variant wraps the text in a div of its own
    return ENTRY.format(
        bare="" if hero else " nophoto",
        photo=PHOTO.format(src=hero.group(1)) if hero else "",
        open_text="\t\t\t<div>\n" if hero else "",
        close_text="\t\t\t</div>\n" if hero else "",
        program=MODAL.format(works=works) if works else "\n",
        **{k: event[k] for k in ("year", "month", "days", "title", "part_of", "place")})


def add_entry(src, event):
    """Newest first inside its year, which is where the year block starts."""
    head = re.search(r'id="y%d"[^>]*>\s*\n\s*%d\s*\n\s*</h1>\s*\n\s*<div class="calendarpast"[^>]*>\n'
                     % (event["year"], event["year"]), src)
    if not head:
        sys.exit("  !! no %d block in archive.html" % event["year"])
    at = head.end()
    return src[:at] + entry(event) + src[at:]


def relink(event):
    """Pages that pointed at the concert now point at the record of it."""
    touched = []
    for path in (sorted(glob.glob("*.html")) + sorted(glob.glob("*/*.html"))
                 + sorted(glob.glob("news/_posts/*.md"))):
        if path.startswith("archive/"):
            continue
        src = open(path, encoding="utf-8").read()
        depth = "../" if "/" in path else ""
        year = "%sarchive.html#y%d" % (depth, event["year"])
        out = src.replace("%sconcerts/%s.html" % (depth, event["slug"]), year)
        if path.startswith("news/_posts/"):
            out = src.replace("concerts/%s.html" % event["slug"],
                              "archive.html#y%d" % event["year"])
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
        archive = add_entry(archive, event)
        calendar = calendar.replace(event["row"], "\n")
        moved = relink(event)
        os.remove("concerts/%s.html" % event["slug"])
        print("%s -> archive.html, %d (%d work(s))%s" % (
            event["slug"], event["year"], len(event["program"]),
            ("   relinked: " + ", ".join(moved)) if moved else ""))

    open("archive.html", "w", encoding="utf-8").write(archive)
    open("concerts.html", "w", encoding="utf-8").write(calendar)
    print("\nNow run: python3 tools/sync_next_event.py && python3 tools/link_performer_bios.py"
          " && python3 tools/build_news.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
