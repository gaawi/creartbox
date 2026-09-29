#!/usr/bin/env python3
"""Keep News in the navigation and in the footer, on every page.

    python3 tools/sync_nav.py            # add it where it is missing
    python3 tools/sync_nav.py --check    # fail if a page is missing it

The site has two shapes of navigation strip: the long one with
submenus on the top-level pages, and the plain one on concert, archive
and artist pages. Both end with Donate, so the News item goes in front
of it, at whatever depth the file lives.

The templates inside tools/*.py are swept too, so a generated page is
not rebuilt without it.
"""

import glob
import re
import sys

ITEM = "News"
PAGE = "news.html"

# <div class="nav-item"><a href="../support.html">Donate</a></div>
ONE_LINE = re.compile(
    r'([ \t]*)<div class="nav-item"><a href="((?:\.\./)*)support\.html">Donate</a></div>')
# <div class="nav-item">\n  <a href="support.html">Donate</a>  (then a submenu)
MULTI = re.compile(
    r'([ \t]*)<div class="nav-item">\n[ \t]*<a href="((?:\.\./)*)support\.html">Donate</a>')

HAS_NAV = re.compile(r'<a href="(?:\.\./)*news\.html"(?: class="active")?>News</a>')
ABOUT_LI = re.compile(r'<li><a href="((?:\.\./)*)about\.html">About</a></li>')
HAS_FOOT = re.compile(r'<li><a href="(?:\.\./)*news\.html">News</a></li>')


def add_nav(src):
    if HAS_NAV.search(src) or "nav-strip-inner" not in src:
        return src

    def one(m):
        pad, prefix = m.group(1), m.group(2)
        return ('{pad}<div class="nav-item"><a href="{p}{page}">{item}</a></div>\n'
                .format(pad=pad, p=prefix, page=PAGE, item=ITEM) + m.group(0))

    def multi(m):
        pad, prefix = m.group(1), m.group(2)
        return ('{pad}<div class="nav-item">\n{pad}  <a href="{p}{page}">{item}</a>\n'
                '{pad}</div>\n'.format(pad=pad, p=prefix, page=PAGE, item=ITEM) + m.group(0))

    out = ONE_LINE.sub(one, src, count=1)
    if out == src:
        out = MULTI.sub(multi, src, count=1)
    return out


def add_foot(src):
    if HAS_FOOT.search(src):
        return src
    return ABOUT_LI.sub(
        lambda m: m.group(0) + '<li><a href="{}{}">{}</a></li>'.format(
            m.group(1), PAGE, ITEM),
        src, count=1)


def files():
    return (sorted(glob.glob("*.html"))
            + sorted(glob.glob("*/*.html"))
            + sorted(glob.glob("tools/*.py")))


def main():
    check = "--check" in sys.argv
    stale = []

    for path in files():
        if path.endswith("build_news.py") or path.endswith("sync_nav.py"):
            continue
        src = open(path, encoding="utf-8").read()
        out = add_foot(add_nav(src))
        if out != src:
            stale.append(path)
            if not check:
                open(path, "w", encoding="utf-8").write(out)

    if check:
        if stale:
            print("News is missing from {} file(s):".format(len(stale)))
            for p in stale[:6]:
                print("  -", p)
            print("\nRun: python3 tools/sync_nav.py")
            return 1
        print("News is in the navigation everywhere")
    else:
        print("News added to %d file(s)" % len(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
