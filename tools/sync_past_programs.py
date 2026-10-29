#!/usr/bin/env python3
"""Keep the catalogue of past programmes fed from the archive.

    python3 tools/sync_past_programs.py          # append what is missing
    python3 tools/sync_past_programs.py --check  # list what is missing

`data/programs-past.txt` is the catalogue the presenters page prints:
every programme the ensemble has played, with its works, movements and
running times, so that a presenter can see what can be revived. The
file is **hand-edited and never rewritten**. This tool only ever adds
blocks for programmes that are in the archive and not yet in the file,
at the end, so a title you renamed or a block you reordered stays as
you left it. Delete a block and it comes back on the next run; comment
its title out with `#skip ` and it does not.

The archive holds the same programme in two shapes, both read here:

- `archive/<slug>.html` carries a `.pgm-list`, a flat run of rows where
  a row with only a composer opens a composer, a row with only a work
  is a work under it, and a work in italics is a movement. This is the
  richer shape: it has the movements.
- `archive.html` carries older entries behind a "View Program" button,
  as `<strong>Composer</strong><br>Work<em>scoring</em>[minutes]`.
  This shape has the scoring, which the other one does not.

Where a title appears in both, the one with more works wins.
"""

import glob
import html
import os
import re
import sys

DATA = "data/programs-past.txt"
ARCHIVE = "archive.html"

HEADER = """\
# Past programmes, as they are offered to presenters.
#
# One block per programme. The first line of a block is the programme,
# the indented lines under it are what was played, in order:
#
#   Title | years | where it was played | formation | number
#     Composer name
#     - Work | scoring | minutes
#     -- I. Movement | | minutes
#
# A line under a title is a composer unless it starts with "- " (a work)
# or "-- " (a movement of the work above it). Scoring and minutes may be
# left empty, and trailing empty fields may be dropped.
#
# This file is hand-edited. Nothing rewrites it: rename a programme,
# reorder the blocks, drop a work, and it stays that way.
# tools/sync_past_programs.py appends programmes found in the archive
# that are not here yet, at the end. To keep one out for good, put
# "#skip " in front of its title line.
"""


def clean(fragment):
    # a space for the tag, not nothing: in the archive an <em> sits
    # against the title, and stripping it bare gives "Piecesfor viola"
    txt = re.sub(r"<[^>]+>", " ", fragment or "")
    txt = re.sub(r"\s+", " ", html.unescape(txt).replace("\u00a0", " ")).strip()
    # some composers carry a trailing asterisk that nothing on the site
    # explains; it is not carried into the catalogue
    return re.sub(r"\s*\*\s*$", "", txt)


def key(title):
    return re.sub(r"[^a-z0-9]+", "", (title or "").lower())


# ------------------------------------------------------------- the file

def read_blocks(path=DATA):
    """Every block in the catalogue, in file order."""
    if not os.path.exists(path):
        return []
    blocks = []
    for line in open(path, encoding="utf-8"):
        raw = line.rstrip("\n")
        if not raw.strip():
            continue
        if raw.startswith("#skip "):
            blocks.append({"title": raw[6:].split("|")[0].strip(), "skip": True,
                           "years": "", "where": "", "formation": "",
                           "number": "", "rows": []})
            continue
        if raw.lstrip().startswith("#"):
            continue
        if raw[:1] in (" ", "\t"):
            if not blocks:
                continue
            body = raw.strip()
            if body.startswith("-- "):
                kind, body = "movement", body[3:]
            elif body.startswith("- "):
                kind, body = "work", body[2:]
            else:
                kind = "composer"
            fields = [f.strip() for f in body.split("|")]
            fields += [""] * (3 - len(fields))
            blocks[-1]["rows"].append((kind, fields[0], fields[1], fields[2]))
        else:
            fields = [f.strip() for f in raw.split("|")]
            fields += [""] * (5 - len(fields))
            blocks.append({"title": fields[0], "years": fields[1], "where": fields[2],
                           "formation": fields[3], "number": fields[4],
                           "skip": False, "rows": []})
    return blocks


def render(block):
    head_ = [block["title"], block["years"], block["where"],
             block.get("formation", ""), block.get("number", "")]
    while head_ and not head_[-1]:
        head_.pop()
    out = [" | ".join(head_)]
    for kind, name, scoring, mins in block["rows"]:
        prefix = {"composer": "  ", "work": "  - ", "movement": "  -- "}[kind]
        tail = ""
        if mins or scoring:
            tail = " | %s | %s" % (scoring, mins)
            tail = re.sub(r"(\s*\|\s*)+$", "", tail)
        out.append(prefix + name + tail)
    return "\n".join(out)


# ---------------------------------------------------------- the archive

def entry_venues():
    """The venue each archive.html entry shows, by title: the page's own
    description line leaves it empty often enough to be worth the look."""
    out = {}
    if not os.path.exists(ARCHIVE):
        return out
    src = open(ARCHIVE, encoding="utf-8").read()
    for chunk in re.split(r'(?=<div class="eventpast)', src)[1:]:
        head = re.search(r"<h3>\s*(.*?)\s*</h3>", chunk, re.S)
        place = re.search(r'<h5 class="address">(.*?)</h5>', chunk, re.S)
        if head and place and clean(head.group(1)) and clean(place.group(1)):
            out.setdefault(key(clean(head.group(1))), clean(place.group(1)))
    return out


def from_pages():
    """Programmes from archive/<slug>.html, which carry the movements."""
    found = {}
    venues = entry_venues()
    for path in sorted(glob.glob("archive/*.html")):
        src = open(path, encoding="utf-8").read()
        block = re.search(r'<ul class="pgm-list">(.*?)</ul>', src, re.S)
        if not block:
            continue
        title = re.search(r'<h1 class="event-title">(.*?)</h1>', src, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', src)
        when = re.search(r"-\s+[A-Z][a-z]+\.? \d{1,2}, (\d{4})\.\s*(.*?)\.\s*CreArtBox archive",
                         html.unescape(desc.group(1)) if desc else "")
        # Some archive pages put the composer in the work span and leave
        # every composer span empty. Those lists cannot be read apart into
        # composers, works and movements, so they are left to the modal in
        # archive.html, which keeps the two separate.
        if not re.search(r'<span class="pgm-composer">\s*\S', block.group(1)):
            continue

        rows = []
        last = ""
        for li in re.findall(r"<li[^>]*>(.*?)</li>", block.group(1), re.S):
            composer = re.search(r'<span class="pgm-composer">(.*?)</span>', li, re.S)
            work = re.search(r'<span class="pgm-work">(.*?)</span>', li, re.S)
            c = clean(composer.group(1).split('<span class="pgm-tag">')[0]) if composer else ""
            w_raw = work.group(1) if work else ""
            mins = re.search(r"\[(\d+)\s*['’]?\]", clean(w_raw))
            w = re.sub(r"\[\d+\s*['’]?\]", "", clean(w_raw)).strip()
            # a row may carry the composer alone (opening a composer), the
            # work alone (under whichever composer is open), or both
            if c and not w:
                rows.append(("composer", c, "", ""))
                last = c
            elif w:
                kind = "movement" if re.search(r"<i>|<em>", w_raw) else "work"
                if c and c != last:
                    rows.append(("composer", c, "", ""))
                    last = c
                rows.append((kind, w, "", mins.group(1) if mins else ""))
        if rows and any(k == "work" for k, *_ in rows):
            name = clean(title.group(1)) if title else os.path.basename(path)
            where = (when.group(2).strip() if when else "") or venues.get(key(name), "")
            found.setdefault(key(name), {
                "title": name, "years": when.group(1) if when else "",
                "where": where, "formation": "", "rows": rows})
    return found


def from_modals():
    """Older programmes, behind the View Program button in archive.html."""
    found = {}
    if not os.path.exists(ARCHIVE):
        return found
    src = open(ARCHIVE, encoding="utf-8").read()
    for chunk in re.split(r'(?=<div class="eventpast)', src)[1:]:
        head = re.search(r"<h3>\s*(.*?)\s*</h3>", chunk, re.S)
        body = re.search(r'<div class="modal-content">(.*?)</div>\s*</div>', chunk, re.S)
        if not (head and body):
            continue
        year = re.search(r'<span class="yearpast">([^<]*)</span>', chunk)
        where = re.search(r"<h5>\s*<i[^>]*></i>(.*?)</h5>", chunk, re.S)
        rows = []
        for m in re.finditer(r"<strong>(.*?)</strong>\s*<br>\s*(.*?)"
                             r"(?=<p>|</p>|<br>\s*<strong>|$)", body.group(1), re.S):
            composer = clean(m.group(1))
            rest = m.group(2)
            scoring = re.search(r"<em>(.*?)</em>", rest, re.S)
            mins = re.search(r"\[(\d+)\s*['’]?\]", clean(rest))
            work = re.sub(r"\[\d+\s*['’]?\]", "",
                          clean(re.sub(r"<em>.*?</em>", "", rest, flags=re.S))).strip()
            if not (composer and work):
                continue
            rows.append(("composer", composer, "", ""))
            rows.append(("work", work,
                         clean(scoring.group(1)).lstrip("for ").strip() if scoring else "",
                         mins.group(1) if mins else ""))
        if rows:
            name = clean(head.group(1))
            found.setdefault(key(name), {
                "title": name, "years": year.group(1) if year else "",
                "where": clean(where.group(1)) if where else "",
                "formation": "", "rows": rows})
    return found


def candidates():
    pages, modals = from_pages(), from_modals()
    out = dict(modals)
    for k, v in pages.items():
        here = out.get(k)
        # a tie goes to the page, which is the source that has the movements
        if not here or sum(1 for r in v["rows"] if r[0] == "work") >= \
                sum(1 for r in here["rows"] if r[0] == "work"):
            # keep the years and the venue of whichever source has them
            if here:
                v = dict(v, years=v["years"] or here["years"],
                         where=v["where"] or here["where"])
            out[k] = v
    return out


def main():
    check = "--check" in sys.argv
    have = {key(b["title"]) for b in read_blocks()}
    missing = [v for k, v in candidates().items() if k not in have]
    missing.sort(key=lambda v: (v["years"], v["title"]), reverse=True)

    if check:
        if missing:
            print("{} archive programme(s) are not in {}:".format(len(missing), DATA))
            for v in missing[:10]:
                print("  - %s (%s)" % (v["title"], v["years"] or "no year"))
            print("\nRun: python3 tools/sync_past_programs.py")
            return 1
        print("every archive programme is in the catalogue (%d block(s))"
              % len(read_blocks()))
        return 0

    if not missing:
        print("nothing to add; the catalogue holds %d programme(s)" % len(read_blocks()))
        return 0

    os.makedirs("data", exist_ok=True)
    new = os.path.exists(DATA) is False
    with open(DATA, "a", encoding="utf-8") as fh:
        if new:
            fh.write(HEADER)
        for v in missing:
            fh.write("\n" + render(v) + "\n")
    print("added %d programme(s) to %s" % (len(missing), DATA))
    for v in missing[:8]:
        print("  +", v["title"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
