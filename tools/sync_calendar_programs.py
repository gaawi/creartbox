#!/usr/bin/env python3
"""Keep the calendar index programme in sync with each concert page.

The programme shown for a row in concerts.html is generated from that
concert's own page, so the two can never drift apart. Run it after editing
any programme:

    python3 tools/sync_calendar_programs.py            # rewrite the index
    python3 tools/sync_calendar_programs.py --check    # fail if out of sync

Rows whose concert page has no structured programme (a residency, or a
date not yet programmed) are left alone; their list is marked
data-program-manual in concerts.html. Where nothing is known, the row
carries no programme line at all - the site does not announce absences.
"""

import os
import re
import sys

INDEX = "concerts.html"

ROW_RE = re.compile(r'<tr[^>]* data-concert-series="[^"]+">.*?</tr>', re.S)
WHEN_RE = re.compile(
    r'<div class="meta-h">When</div>\s*<div class="meta-v">([^<]*)</div>', re.S)
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\s*(?:am|pm)\b", re.I)
ROW_TIME_RE = re.compile(r'<span class="row-time">.*?</span>', re.S)
SERIES_RE = re.compile(r'class="event-series">([^<]*)', re.S)
ROW_LABEL_RE = re.compile(r'(<div class="label" style="margin-bottom:8px">)(.*?)(</div>)', re.S)
ROW_NEW_RE = re.compile(r'\s*<span class="row-new">.*?</span>', re.S)
TICKETS_RE = re.compile(r'href="(https://www\.eventbrite\.com/e/[^"]+)"[^>]*class="btn btn-ticket"')
ACTIONS_RE = re.compile(r'(<td class="actions">)(.*?)(</td>)', re.S)
ROW_TICKETS_RE = re.compile(r'\s*<a class="btn[^"]*\brow-tickets\b[^"]*".*?</a>', re.S)
EXPLORE_CLASS_RE = re.compile(r'(<a href="[^"]*" class=")btn[^"]*(">Explore</a>)')
# the ensemble's own productions, as opposed to touring an existing programme
NEW_PRODUCTION_SERIES = "New York Series"
HREF_RE = re.compile(r'class="title-cell"><a href="([^"]+)"')
TITLE_RE = re.compile(r'class="title-cell"><a[^>]*>([^<]+)</a>')
UL_RE = re.compile(r'<ul[^>]*>.*?</ul>', re.S)
PROGRAM_RE = re.compile(r'<section class="event-program">(.*?)</section>', re.S)
ITEM_RE = re.compile(
    r'<li><span class="pgm-composer">(.*?)</span>'
    r'<span class="pgm-work">(.*?)</span></li>',
    re.S,
)
# durations and the open-call / premiere tag belong to the concert page only
MINS_RE = re.compile(r'\s*<span class="pgm-mins">.*?</span>', re.S)
TAG_RE = re.compile(r'<span class="pgm-tag">.*?</span>', re.S)


def strip_tags(fragment):
    return re.sub(r"<[^>]+>", "", fragment).strip()


def programme_of(page):
    """Return [(composer, work)] for a concert page, or None if it has none."""
    if not os.path.exists(page):
        return None
    section = PROGRAM_RE.search(open(page, encoding="utf-8").read())
    if not section or "pgm-list" not in section.group(1):
        return None
    items = []
    for composer, work in ITEM_RE.findall(section.group(1)):
        items.append(
            (
                strip_tags(TAG_RE.sub("", composer)),
                strip_tags(MINS_RE.sub("", work)),
            )
        )
    return items or None


def time_of(page):
    """The clock time from the concert page's own When row, if it has one."""
    if not os.path.exists(page):
        return None
    when = WHEN_RE.search(open(page, encoding="utf-8").read())
    if not when:
        return None
    found = TIME_RE.search(when.group(1))
    return found.group(0) if found else None


def sync_time(row, page):
    """Put that time in the row's date cell, so the two cannot disagree."""
    wanted = time_of(page)
    current = ROW_TIME_RE.search(row)
    if not wanted:
        # the page dropped its time: take it out of the index too
        return ROW_TIME_RE.sub("", row) if current else row
    cell = '<span class="row-time">{}</span>'.format(wanted)
    if current:
        return row.replace(current.group(0), cell, 1)
    # sits under the weekday, at the end of the date cell
    return row.replace("</td>", cell + "</td>", 1)


def is_new_production(page):
    """True for the ensemble's own New York Series productions."""
    if not os.path.exists(page):
        return False
    series = SERIES_RE.search(open(page, encoding="utf-8").read())
    return bool(series) and series.group(1).strip().startswith(NEW_PRODUCTION_SERIES)


def sync_new_production(row, page):
    """Mark those rows in the calendar, and only those.

    The row carries a flag as well as the chip, so the amber edge is a
    plain attribute selector rather than :has() on the chip.
    """
    new = is_new_production(page)
    row = row.replace(" data-new-production", "", 1)
    if new:
        row = row.replace("<tr data-concert-series=",
                          "<tr data-new-production data-concert-series=", 1)
    label = ROW_LABEL_RE.search(row)
    if not label:
        return row
    text = ROW_NEW_RE.sub("", label.group(2))
    if new:
        text += ' <span class="row-new">New production</span>'
    return row.replace(label.group(0), label.group(1) + text + label.group(3), 1)


def sync_tickets(row, page):
    """Offer tickets from the calendar as soon as the concert page does."""
    url = None
    if os.path.exists(page):
        found = TICKETS_RE.search(open(page, encoding="utf-8").read())
        url = found.group(1) if found else None
    cell = ACTIONS_RE.search(row)
    if not cell:
        return row
    body = ROW_TICKETS_RE.sub("", cell.group(2))
    # Explore is the only thing left in the cell, so its class is set
    # outright rather than by swapping whichever variant is there now -
    # that swap was matching the tickets button and duplicating it.
    # Where a seat can be bought, buying is the loud button and Explore
    # steps back to an outline. Everywhere else Explore keeps the stamp.
    explore = "btn btn-s" if url else "btn btn-stamp btn-s"
    body = EXPLORE_CLASS_RE.sub(lambda m: m.group(1) + explore + m.group(2), body, count=1)
    if url:
        # The button says where it goes: the reader leaves the site and
        # lands on a vendor's checkout. TICKETS_RE only matches Eventbrite,
        # so naming it here cannot be wrong.
        body += ('<a class="btn btn-stamp btn-s row-tickets" href="{}" target="_blank" '
                 'rel="noopener">Tickets &#183; Eventbrite <span class="ar">&#8594;</span></a>'.format(url))
    return row.replace(cell.group(0), cell.group(1) + body + cell.group(3), 1)


def render(items):
    lis = "".join(
        '<li><span class="rp-composer">{}</span>'
        '<span class="rp-work">{}</span></li>'.format(c, w)
        for c, w in items
    )
    return '<ul class="row-program">' + lis + "</ul>"


def main():
    check = "--check" in sys.argv
    src = open(INDEX, encoding="utf-8").read()
    out = src
    synced, manual, drifted = [], [], []

    for match in ROW_RE.finditer(src):
        row = match.group(0)
        href = HREF_RE.search(row)
        if not href:
            continue
        title = TITLE_RE.search(row)
        title = title.group(1) if title else href.group(1)

        # both of these are synced whether or not the programme is generated
        marked = sync_new_production(row, href.group(1))
        if marked != row:
            out = out.replace(row, marked, 1)
            row = marked

        ticketed = sync_tickets(row, href.group(1))
        if ticketed != row:
            out = out.replace(row, ticketed, 1)
            row = ticketed

        timed = sync_time(row, href.group(1))
        if timed != row:
            out = out.replace(row, timed, 1)
            row = timed

        items = programme_of(href.group(1))
        if items is None:
            manual.append(title)
            continue

        wanted = render(items)
        if not UL_RE.search(row):
            print("  !! no programme list found in the row for", title)
            continue
        current = UL_RE.search(row).group(0)
        if current != wanted:
            drifted.append(title)
        out = out.replace(row, UL_RE.sub(wanted, row, count=1), 1)
        synced.append(title)

    if check:
        if drifted:
            print("OUT OF SYNC with the concert pages:")
            for t in drifted:
                print("  -", t)
            print("\nRun: python3 tools/sync_calendar_programs.py")
            return 1
        print("in sync: {} generated, {} manual".format(len(synced), len(manual)))
        return 0

    if out != src:
        open(INDEX, "w", encoding="utf-8").write(out)
    print("generated {} programme(s): {}".format(len(synced), ", ".join(synced)))
    if manual:
        print("left manual ({}): {}".format(len(manual), ", ".join(manual)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
