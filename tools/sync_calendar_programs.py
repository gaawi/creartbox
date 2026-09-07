#!/usr/bin/env python3
"""Keep the calendar index programme in sync with each concert page.

The programme shown for a row in concerts.html is generated from that
concert's own page, so the two can never drift apart. Run it after editing
any programme:

    python3 tools/sync_calendar_programs.py            # rewrite the index
    python3 tools/sync_calendar_programs.py --check    # fail if out of sync

Rows whose concert page has no structured programme (a residency, or a
date whose programme is not announced yet) are left alone; their list is
marked data-program-manual in concerts.html.
"""

import os
import re
import sys

INDEX = "concerts.html"

ROW_RE = re.compile(r'<tr data-concert-series="[^"]+">.*?</tr>', re.S)
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
