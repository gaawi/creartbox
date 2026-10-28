#!/usr/bin/env python3
"""Give every entry in the archive a way into its own page.

    python3 tools/link_archive_entries.py          # add the missing links
    python3 tools/link_archive_entries.py --check  # fail if any are missing

`archive.html` lists 102 performances and `archive/` holds a page for
each, with the programme, the photographs and the structured data. Only
58 of the entries carried a "View more" button, so 47 of those pages
could not be reached by clicking anything, anywhere on the site. They
were in the sitemap and nowhere else.

An entry is matched to its page by title, year and month, which is what
the page filenames are built from. Where two performances share all
three - Paris a.m. twice in December 2013 - the day decides. Anything
still ambiguous is left alone and reported rather than guessed at.
"""

import glob
import html
import os
import re
import sys

PAGE = "archive.html"
LINK = ('\n\t\t\t\t<div class="explore">\n'
        '\t\t\t\t\t<a class="button" href="archive/{slug}">View more</a>\n'
        '\t\t\t\t</div>')

MONTHS = ("jan feb mar apr may jun jul aug sep oct nov dec").split()


def plain(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment or ""))).strip()


def norm(title):
    return re.sub(r"[^a-z0-9]+", "", (title or "").lower())


def read_date(text):
    """(month, day, year) from the line the archive writes.

    Four shapes are in use: "Jun 6, 2025", "Jul 1-7, 2019",
    "August 2021" and "8 - 13 August 2022".
    """
    m = re.search(r"-\s+([A-Z][a-z]{2})[a-z]*\.?\s+"
                  r"(?:(\d{1,2})(?:\s*[-\u2013]\s*\d{1,2})?,\s*)?(\d{4})\.", text)
    if m:
        return m.group(1).lower(), m.group(2) or "", m.group(3)
    m = re.search(r"-\s+(\d{1,2})(?:\s*[-\u2013]\s*\d{1,2})?\s+"
                  r"([A-Z][a-z]{2})[a-z]*\.?\s+(\d{4})", text)
    if m:
        return m.group(2).lower(), m.group(1), m.group(3)
    return None


def pages():
    """Every archive page, by title, year and month, with the day if known.

    The second index is by title alone, for the handful of pages whose
    date line cannot be read - a tour across two years, say.
    """
    out, by_title = {}, {}
    for path in sorted(glob.glob("archive/*.html")):
        src = open(path, encoding="utf-8").read()
        title = re.search(r'<h1 class="event-title">(.*?)</h1>', src, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', src)
        if not title:
            continue
        key = norm(plain(title.group(1)))
        by_title.setdefault(key, []).append(os.path.basename(path))
        when = read_date(html.unescape(desc.group(1)) if desc else "")
        if not when:
            continue
        month, day, year = when
        out.setdefault((key, year, month), []).append((day, os.path.basename(path)))
    return out, by_title


def entries(src):
    """Each entry of the archive, as (start, end) offsets into the page."""
    spans = []
    for m in re.finditer(r'<div class="eventpast', src):
        spans.append(m.start())
    spans.append(len(src))
    return [(spans[i], spans[i + 1]) for i in range(len(spans) - 1)]


def insert_at(chunk):
    """Where the button goes: after the venue, and after the programme
    modal when the entry has one, so that it stays the last thing."""
    modal = re.search(r'<div class="modal modal_multi">', chunk)
    if modal:
        depth, i = 0, modal.start()
        for m in re.finditer(r"<div\b|</div>", chunk[modal.start():]):
            depth += 1 if m.group(0).startswith("<div") else -1
            if depth == 0:
                i = modal.start() + m.end()
                break
        return i
    last_h5 = None
    for m in re.finditer(r"</h5>", chunk):
        last_h5 = m.end()
    if last_h5:
        return last_h5
    m = re.search(r"</h3>", chunk)
    return m.end() if m else None


def main():
    check = "--check" in sys.argv
    src = open(PAGE, encoding="utf-8").read()
    known, by_title = pages()

    titles = {}
    for start, end in entries(src):
        t = re.search(r"<h3>\s*(.*?)\s*</h3>", src[start:end], re.S)
        if t:
            k = norm(plain(t.group(1)))
            titles[k] = titles.get(k, 0) + 1

    added, missing, ambiguous, elsewhere, repointed = [], [], [], [], []
    out, cursor = [], 0
    for start, end in entries(src):
        chunk = src[start:end]
        out.append(src[cursor:start])
        cursor = end
        title = re.search(r"<h3>\s*(.*?)\s*</h3>", chunk, re.S)
        year = re.search(r'<span class="yearpast">([^<]*)</span>', chunk)
        month = re.search(r'<span class="monthpast">([^<]*)</span>', chunk)
        day = re.search(r'<span class="daypast">([^<]*)</span>', chunk)
        name = plain(title.group(1)) if title else ""

        linked = re.search(r'href="archive/([a-z0-9-]+\.html)"', chunk)
        # an entry whose only button goes somewhere else - the festival
        # site, a news post - keeps it: two buttons with the same label
        # and different targets is worse than one
        if ('class="explore"' in chunk and not linked) or not (title and year and month):
            if 'class="explore"' in chunk and not linked:
                elsewhere.append(name)
            out.append(chunk)
            continue

        key = (norm(name), year.group(1).strip(), month.group(1).strip().lower()[:3])
        found = known.get(key, [])
        if not found:
            # The date on the entry and the date on the page disagree now
            # and then, by a month. A title that belongs to exactly one
            # page and exactly one entry can still only mean one thing.
            same = by_title.get(norm(name), [])
            if len(same) == 1 and titles[norm(name)] == 1:
                found = [("", same[0])]
        if not found:
            missing.append("%s (%s %s)" % (name, month.group(1), year.group(1)))
            out.append(chunk)
            continue
        if len(found) > 1:
            first = re.match(r"\d+", day.group(1).strip()) if day else None
            exact = [s for d, s in found if first and d and d == first.group(0)]
            if len(exact) != 1:
                ambiguous.append("%s (%s %s)" % (name, month.group(1), year.group(1)))
                out.append(chunk)
                continue
            slug = exact[0]
        else:
            slug = found[0][1]

        if linked:
            # Four AWAVE entries and the second Paris a.m. all pointed at a
            # different concert's page, which is worse than pointing at
            # nothing: the visitor lands on the wrong evening. Repoint only
            # when the page this entry actually matches is not the one the
            # button names, and say so.
            if linked.group(1) != slug:
                chunk = chunk.replace('href="archive/%s"' % linked.group(1),
                                      'href="archive/%s"' % slug, 1)
                repointed.append("%s: %s -> %s" % (name, linked.group(1), slug))
            out.append(chunk)
            continue

        at = insert_at(chunk)
        if at is None:
            missing.append(name + " (nowhere to put the button)")
            out.append(chunk)
            continue
        added.append(name)
        out.append(chunk[:at] + LINK.format(slug=slug) + chunk[at:])
    out.append(src[cursor:])
    new = "".join(out)

    for label, items in (("no page found for", missing),
                         ("more than one page matches", ambiguous),
                         ("View more already points elsewhere on", elsewhere),
                         ("pointed at the wrong page,", repointed)):
        if items:
            print("%s %d entr%s:" % (label, len(items), "y" if len(items) == 1 else "ies"))
            for x in items[:8]:
                print("   -", x)

    if check:
        if added or repointed:
            added = added + repointed
            print("%d archive entr%s cannot be reached by clicking:"
                  % (len(added), "y" if len(added) == 1 else "ies"))
            for x in added[:8]:
                print("   -", x)
            print("\nRun: python3 tools/link_archive_entries.py")
            return 1
        print("every archive entry that has a page links to it")
        return 0

    if added or repointed:
        open(PAGE, "w", encoding="utf-8").write(new)
    print("linked %d archive entr%s to their own page, repointed %d"
          % (len(added), "y" if len(added) == 1 else "ies", len(repointed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
