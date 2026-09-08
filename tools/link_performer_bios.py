#!/usr/bin/env python3
"""Normalise the performer lists and link each name to its biography.

Two jobs, both idempotent:

1. Tidy the lists. An old import left many archive pages with the role
   inside the name ("Josefina Urraca, piano" in one span), and a few with
   the name split across two list items ("Guillermo" then "Laporta,
   flute", or "Mathew Cohen" then "viola"). Both are split back into a
   name and a role, so every page shows the same two-column shape.

2. Link the names. A visitor reading a programme should be able to reach
   the player's biography from the name itself, so any name in MEMBERS is
   wrapped in a link to its anchor on the about page.

    python3 tools/link_performer_bios.py            # rewrite the pages
    python3 tools/link_performer_bios.py --check    # fail if out of date

Names not in MEMBERS are left as plain text: the site links to a
biography it has, and stays silent otherwise.
"""

import glob
import re
import sys

# core ensemble -> anchor on about.html
MEMBERS = {
    "Guillermo Laporta": "member-laporta",
    "Josefina Urraca": "member-urraca",
    "Emilie-Anne Gendron": "member-gendron",
    "Matthew Cohen": "member-cohen",
    "Julia Yang": "member-yang",
}

# spellings that drifted from the ones the about page uses
RENAME = {
    "Mathew Cohen": "Matthew Cohen",
    "Emilie Anne Gendron": "Emilie-Anne Gendron",
    "Emilie Anne": "Emilie-Anne",
    "Sarah K Williams": "Sarah K. Williams",
}

LIST_RE = re.compile(r'(<ul class="art-list">)(.*?)(</ul>)', re.S)
LI_RE = re.compile(r"<li>(.*?)</li>", re.S)
NAME_RE = re.compile(r'<span class="art-name">(.*?)</span>', re.S)
ROLE_RE = re.compile(r'<span class="art-role">(.*?)</span>', re.S)
TAGS_RE = re.compile(r"<[^>]+>")
ROLE_ONLY_RE = re.compile(r"[a-z][a-z &]*\Z")
# an instrument or job, with no proper names in it
PLAIN_ROLE_RE = re.compile(r"[A-Za-z\u00c0-\u024f][A-Za-z\u00c0-\u024f\- ]*\Z")


def plain(fragment):
    """The name as text, with any link this script added stripped off."""
    return TAGS_RE.sub("", fragment).strip()


def parse(list_body):
    items = []
    for li in LI_RE.findall(list_body):
        name = NAME_RE.search(li)
        role = ROLE_RE.search(li)
        if not name:
            return None  # a shape this script does not understand
        items.append([plain(name.group(1)), plain(role.group(1)) if role else None])
    return items


def normalise(items):
    """Split "Name, role" apart and rejoin names broken over two items."""
    out = []
    i = 0
    while i < len(items):
        name, role = items[i]
        nxt = items[i + 1] if i + 1 < len(items) else None

        if role is None and nxt and nxt[1] is None and "," not in name:
            follower = nxt[0]
            if ROLE_ONLY_RE.match(follower):
                # "Mathew Cohen" + "viola"
                name, role, i = name, follower, i + 1
            elif "," in follower:
                # "Guillermo" + "Laporta, light, sound and projection design"
                rest, _, tail = follower.partition(",")
                name = (name + " " + rest).strip()
                role = tail.strip()
                i += 1

        if role is None and "," in name:
            # "Josefina Urraca, piano" - the first comma ends the name, so a
            # role that itself contains commas survives intact
            head, _, tail = name.partition(",")
            if head.strip() and tail.strip():
                name, role = head.strip(), tail.strip()

        name = RENAME.get(name, name)
        if role:
            # "Violin" -> "violin", but leave a role that names people or
            # a work alone ("sound art - Coco Moya & Ivan Cebrian")
            if PLAIN_ROLE_RE.match(role):
                role = role.lower()
            if role == "violia":
                role = "viola"  # typo in the original listing
        out.append([name, role])
        i += 1
    return out


def render(items, prefix):
    lis = []
    for name, role in items:
        anchor = MEMBERS.get(name)
        label = name
        if anchor:
            label = '<a href="{}about.html#{}">{}</a>'.format(prefix, anchor, name)
        li = '<li><span class="art-name">{}</span>'.format(label)
        if role:
            li += '<span class="art-role">{}</span>'.format(role)
        lis.append(li + "</li>")
    return "".join(lis)


def main():
    check = "--check" in sys.argv
    changed, skipped = [], []

    for path in sorted(glob.glob("archive/*.html") + glob.glob("concerts/*.html")):
        src = open(path, encoding="utf-8").read()

        def rewrite(match):
            items = parse(match.group(2))
            if items is None:
                skipped.append(path)
                return match.group(0)
            body = render(normalise(items), "../")
            return match.group(1) + body + match.group(3)

        out = LIST_RE.sub(rewrite, src)
        if out != src:
            changed.append(path)
            if not check:
                open(path, "w", encoding="utf-8").write(out)

    if check:
        if changed:
            print("performer lists out of date in {} page(s):".format(len(changed)))
            for p in changed:
                print("  -", p)
            print("\nRun: python3 tools/link_performer_bios.py")
            return 1
        print("performer lists up to date ({} unparsed)".format(len(set(skipped))))
        return 0

    print("rewrote {} page(s)".format(len(changed)))
    for p in changed:
        print("  -", p)
    if skipped:
        print("left alone (unrecognised shape): {}".format(", ".join(sorted(set(skipped)))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
