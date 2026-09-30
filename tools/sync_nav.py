#!/usr/bin/env python3
"""Keep News in the navigation and in the footer, on every page.

    python3 tools/sync_nav.py            # add it where it is missing
    python3 tools/sync_nav.py --check    # fail if a page is missing it

The site has two shapes of navigation strip: the long one with
submenus on the top-level pages, and the plain one on concert, archive
and artist pages. Both end with Donate, so a new item goes in front of
it, at whatever depth the file lives. The strip is full at nine items,
so the presenters page lives in the footer only.

The templates inside tools/*.py are swept too, so a generated page is
not rebuilt without it.
"""

import glob
import re
import sys

# in the navigation strip, in front of Donate
NAV = [("news.html", "News")]
# in the footer, under The Organization: presenters look there, and the
# strip has no room for a tenth item
FOOT = [("news.html", "News"), ("presenters.html", "For presenters")]

# <div class="nav-item"><a href="../support.html">Donate</a></div>
ONE_LINE = re.compile(
    r'([ \t]*)<div class="nav-item"><a href="((?:\.\./)*)support\.html">Donate</a></div>')
# <div class="nav-item">\n  <a href="support.html">Donate</a>  (then a submenu)
MULTI = re.compile(
    r'([ \t]*)<div class="nav-item">\n[ \t]*<a href="((?:\.\./)*)support\.html">Donate</a>')

ABOUT_LI = re.compile(r'<li><a href="((?:\.\./)*)about\.html">About</a></li>')


def has_nav(src, page, item):
    return re.search(r'<a href="(?:\.\./)*{}"(?: class="active")?>{}</a>'.format(
        re.escape(page), re.escape(item)), src) is not None


def has_foot(src, page, item):
    return re.search(r'<li><a href="(?:\.\./)*{}">{}</a></li>'.format(
        re.escape(page), re.escape(item)), src) is not None


def add_nav(src, page, item):
    if has_nav(src, page, item) or "nav-strip-inner" not in src:
        return src

    def one(m):
        pad, prefix = m.group(1), m.group(2)
        return ('{pad}<div class="nav-item"><a href="{p}{page}">{item}</a></div>\n'
                .format(pad=pad, p=prefix, page=page, item=item) + m.group(0))

    def multi(m):
        pad, prefix = m.group(1), m.group(2)
        return ('{pad}<div class="nav-item">\n{pad}  <a href="{p}{page}">{item}</a>\n'
                '{pad}</div>\n'.format(pad=pad, p=prefix, page=page, item=item) + m.group(0))

    out = ONE_LINE.sub(one, src, count=1)
    if out == src:
        out = MULTI.sub(multi, src, count=1)
    return out


def add_foot(src, page, item):
    if has_foot(src, page, item):
        return src
    return ABOUT_LI.sub(
        lambda m: m.group(0) + '<li><a href="{}{}">{}</a></li>'.format(
            m.group(1), page, item),
        src, count=1)


def files():
    return (sorted(glob.glob("*.html"))
            + sorted(glob.glob("*/*.html"))
            + sorted(glob.glob("tools/*.py")))


def main():
    check = "--check" in sys.argv
    stale = []

    for path in files():
        if path.endswith(("build_news.py", "build_presenters.py", "sync_nav.py")):
            continue
        src = open(path, encoding="utf-8").read()
        out = src
        for page, item in NAV:
            out = add_nav(out, page, item)
        for page, item in FOOT:
            out = add_foot(out, page, item)
        if out != src:
            stale.append(path)
            if not check:
                open(path, "w", encoding="utf-8").write(out)

    if check:
        if stale:
            print("A section is missing from {} file(s):".format(len(stale)))
            for p in stale[:6]:
                print("  -", p)
            print("\nRun: python3 tools/sync_nav.py")
            return 1
        print("every section is in the navigation everywhere")
    else:
        print("navigation fixed in %d file(s)" % len(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
