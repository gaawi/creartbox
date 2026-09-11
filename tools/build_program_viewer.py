#!/usr/bin/env python3
"""Turn a concert programme PDF into a page you can read in the browser.

A programme is printed as a saddle-stitched booklet, so it is read in
spreads: the cover alone, then two pages at a time, then the back cover
alone. The viewer does the same on a wide screen and falls back to one
page at a time on a phone.

    python3 tools/build_program_viewer.py            # render and write
    python3 tools/build_program_viewer.py --check    # fail if out of date

Each programme is declared in PROGRAMS below. The pages are rendered
from the PDF itself, so the reader and the download can never show
different things; re-run this after replacing a PDF.

Rendering needs PyMuPDF (pip install pymupdf). Without it --check still
works as long as the images are already on disk.
"""

import html
import os
import sys

PROGRAMS = [
    {
        "slug": "currents-2026",
        "pdf": "downloads/currents-2026-program.pdf",
        "title": "Currents",
        "series": "New York Series · Autumn",
        "when": "October 30, 2026 · 7:30 pm · The DiMenna Center",
        "concert": "concerts/currents-2026.html",
    },
]

ZOOM = 2.5          # 990 x 1530 for a half-letter page: sharp on a 2x screen
QUALITY = 82
THUMB_W = 180


def out_dir(slug):
    return os.path.join("assets/programs", slug)


def render(program, check):
    """Write one JPEG per page plus a thumbnail. Returns (pages, ratio)."""
    import pymupdf

    doc = pymupdf.open(program["pdf"])
    pages = doc.page_count
    rect = doc[0].rect
    ratio = round(rect.width / rect.height, 4)
    size = (round(rect.width * ZOOM), round(rect.height * ZOOM))
    d = out_dir(program["slug"])
    stale = []

    if not check:
        os.makedirs(d, exist_ok=True)

    for i, page in enumerate(doc, 1):
        full = os.path.join(d, "p%02d.jpg" % i)
        thumb = os.path.join(d, "t%02d.jpg" % i)
        if check:
            if not (os.path.exists(full) and os.path.exists(thumb)):
                stale.append(full)
            continue
        pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM))
        pix.pil_save(full, format="JPEG", quality=QUALITY, optimize=True,
                     progressive=True)
        tz = THUMB_W / rect.width
        page.get_pixmap(matrix=pymupdf.Matrix(tz, tz)).pil_save(
            thumb, format="JPEG", quality=78, optimize=True)

    # a page left over from a shorter PDF would keep being served
    if not check:
        for name in sorted(os.listdir(d)):
            n = name[1:3]
            if name[0] in "pt" and n.isdigit() and int(n) > pages:
                os.remove(os.path.join(d, name))

    return pages, ratio, size, stale


def page_html(program, pages, ratio, pw, ph):
    t = html.escape(program["title"])
    pdf = program["pdf"].split("/")[-1]
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t} · Concert programme · CreArtBox</title>
<meta name="description" content="The printed programme for {t}, {when}. Read it here or download the PDF.">
<link rel="icon" type="image/svg+xml" href="../brand/mark-wedge-box.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,300..700;1,300..700&family=Literata:ital,opsz,wght@0,7..72,300..700;1,7..72,300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/styles.css?v=118">
<script id="cb-theme-init">document.documentElement.setAttribute("data-theme","dark");</script>
</head>
<body>

<header class="masthead">
  <div class="masthead-inner">
    <div class="masthead-left"><button class="nav-burger" aria-label="Menu">Menu</button><span class="established">Established 2013, New York City</span></div>
    <a class="masthead-title" href="../index.html"><img class="logo-img" src="../brand/logo-creartbox-reversed.svg" alt="CreArtBox"></a>
    <div class="masthead-right"><a class="masthead-tickets" href="../concerts.html">Get tickets</a></div>
  </div>
  <nav class="nav-strip">
    <div class="nav-strip-inner">
      <div class="nav-item"><a href="../index.html">Home</a></div>
      <div class="nav-item"><a href="../about.html">About</a></div>
      <div class="nav-item"><a href="../concerts.html" class="active">Calendar</a></div>
      <div class="nav-item"><a href="../archive.html">Archive</a></div>
      <div class="nav-item"><a href="../projects.html">Projects</a></div>
      <div class="nav-item"><a href="../opportunities.html">Opportunities</a></div>
      <div class="nav-item"><a href="../media.html">Media</a></div>
      <div class="nav-item"><a href="../support.html">Donate</a></div>
    </div>
  </nav>
</header>

<main>

<section class="pv-page">
  <div class="wrap">
    <a href="../{concert}" class="back-to-archive">&#8592; {t}</a>

    <header class="pv-head">
      <div class="label">Concert programme</div>
      <h1 class="pv-title">{t}</h1>
      <div class="pv-sub">{series} &#183; {when}</div>
    </header>

    <div class="pv" data-program data-pages="{pages}" data-ratio="{ratio}"
         data-pw="{pw}" data-ph="{ph}"
         data-dir="../assets/programs/{slug}" data-title="{t}">
      <div class="pv-stage" data-pv-stage>
        <button type="button" class="pv-nav pv-prev" data-pv-prev aria-label="Previous page"></button>
        <div class="pv-book" data-pv-book></div>
        <button type="button" class="pv-nav pv-next" data-pv-next aria-label="Next page"></button>
      </div>

      <div class="pv-bar">
        <button type="button" class="pv-btn" data-pv-thumbs aria-expanded="false">All pages</button>
        <span class="pv-count" data-pv-count aria-live="polite">1 / {pages}</span>
        <button type="button" class="pv-btn" data-pv-zoom aria-pressed="false">Zoom</button>
        <button type="button" class="pv-btn" data-pv-full>Full screen</button>
        <a class="pv-btn pv-dl" href="../downloads/{pdf}" download>Download PDF</a>
      </div>

      <div class="pv-thumbs" data-pv-strip hidden></div>
      <p class="pv-hint">Use the arrow keys, or swipe. The printed booklet is {pages} pages.</p>
    </div>
  </div>
</section>

</main>

<footer class="colophon">
  <div class="wrap">
    <div class="colophon-grid">
      <div>
        <div class="colophon-mark"><img src="../brand/mark-wedge-amber.svg" alt="CreArtBox" width="52" height="24"></div>
        <p class="colophon-bio">A 501(c)(3) non-profit chamber music and multimedia ensemble. New York · Asturias.</p>
        <p class="colophon-addr">info@creartbox.nyc · 10–48 47th Road, Unit 1, Queens, NY 11101</p>
      </div>
      <div><h4>Program</h4><ul><li><a href="../concerts.html">Calendar</a></li><li><a href="../archive.html">Archive of Performances</a></li><li><a href="../projects.html">Productions</a></li><li><a href="https://festivaladar.com" target="_blank" rel="noopener">Festival ADAR</a></li><li><a href="https://apps.apple.com/us/app/creartbox/id6746415261" target="_blank" rel="noopener">iOS app · App Store</a></li></ul></div>
      <div><h4>The Organization</h4><ul><li><a href="../about.html">About</a></li><li><a href="../opportunities.html">Opportunities</a></li><li><a href="../brand.html">Brand &amp; press kit</a></li><li><a href="../media.html#magazine">CreArt Magazine</a></li></ul></div>
      <div><h4>Give</h4><ul><li><a href="../support.html">Donate</a></li></ul></div>
    </div>
    <div class="colophon-bot"><span>© CreArtBox, Inc. 2013–2027 · 501(c)(3) non-profit</span></div>
  </div>
</footer>

<script src="../assets/site.js?v=38"></script>
<script src="../assets/program-viewer.js?v=1"></script>
</body>
</html>
""".format(t=t, pages=pages, ratio=ratio, pw=pw, ph=ph,
           slug=program["slug"], pdf=pdf,
           concert=program["concert"],
           series=html.escape(program["series"]),
           when=html.escape(program["when"]))


def main():
    check = "--check" in sys.argv
    stale = []

    for program in PROGRAMS:
        if not os.path.exists(program["pdf"]):
            print("  !! missing", program["pdf"])
            return 1
        try:
            pages, ratio, size, missing = render(program, check)
        except ImportError:
            if not check:
                print("PyMuPDF is needed to render pages: pip install pymupdf")
                return 1
            # checking without it: trust what is on disk
            d = out_dir(program["slug"])
            pages = len([f for f in os.listdir(d) if f.startswith("p")])
            ratio, size, missing = 0.6471, (990, 1530), []
        stale += missing

        path = os.path.join("programs", program["slug"] + ".html")
        wanted = page_html(program, pages, ratio, size[0], size[1])
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if current != wanted:
            stale.append(path)
            if not check:
                os.makedirs("programs", exist_ok=True)
                open(path, "w", encoding="utf-8").write(wanted)
        if not check:
            print("%s: %d pages" % (program["slug"], pages))

    if check:
        if stale:
            print("programme viewer out of date ({} file(s)):".format(len(stale)))
            for p in stale[:6]:
                print("  -", p)
            print("\nRun: python3 tools/build_program_viewer.py")
            return 1
        print("programme viewers up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
