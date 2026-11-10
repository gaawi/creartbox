#!/usr/bin/env python3
"""The archive page of a production, with its photographs.

    python3 tools/build_photo_page.py            # write the pages
    python3 tools/build_photo_page.py --check    # fail if one is out of date

When a concert is over, `archive_past.py` files it as an entry in
`archive.html` and deletes the concert page. That is enough for a date
with nothing to show. A production that was photographed deserves a
page of its own, the shape the archive has used since Threshold: four
photographs across the top, the text and the performers, the programme
in the sidebar, and behind one button every web-size frame and every
original.

The photographs live on Bunny, under
`creartbox-archive.b-cdn.net/archive-creartbox/<folder>/`, in `web/`
and in `hd/` or `hr/`. Nothing is copied into this repository: the
list of filenames is in `data/archive-photos.txt`, so the page can be
rebuilt without credentials, and dropping a frame from the gallery is
deleting a line.

The text, the performers and the programme come from the concert's own
page, taken out of git at the revision named in the table below, since
the live file is deleted the moment the date is archived.
"""

import html
import os
import re
import subprocess
import sys

CDN = "https://creartbox-archive.b-cdn.net/archive-creartbox"
DATA = "data/archive-photos.txt"

# One row per production with a gallery. `source` is the concert page as
# it stood before archive_past.py deleted it: <rev>:<path>.
PAGES = [
    {
        "slug": "currents-2026-10",
        "title": "Currents",
        "folder": "2026-10-30-currents-photos",
        "originals": "hd",
        "source": "bbe2671^:concerts/currents-2026.html",
        "part_of": "New York Series · Autumn",
        "month": "Oct", "day": "30", "year": "2026",
        "venue": "The DiMenna Center · 450 W 37th St",
        "place": "New York, NY",
        "booklet": "programs/currents-2026.html",
        # The first three are the photographer's own choice. They happen
        # to fall into the rhythm the row wants anyway -- wide, close,
        # wide -- so the fourth is the one that closes an evening:
        #   0589     black and white, the hall in silhouette and the
        #            piano alone under the lights
        #   0602     the pianist in profile, warm, close
        #   0635     the spiral projections across the back wall: the
        #            frame that says what a CreArtBox evening is
        #   MG_0661  the four of them at the bow
        "top": ["_DSC0589.jpg", "_DSC0602.jpg", "_DSC0635.jpg", "_MG_0661.jpg"],
        # and the one that stands for the night in archive.html. The
        # projections, because a thumbnail has to be read at a glance and
        # those spirals survive being made small, where five figures on a
        # wide stage do not.
        "cover": "_DSC0635.jpg",
        # Six more in an even grid, above the button to the whole set.
        # The establishing shot of the quintet lives here now, with the
        # black and white and the details:
        #   0634     the quintet on stage
        #   MG_0437  the pianist, black and white
        #   0483     her hands on the keys
        #   MG_0531  the cellist mid-bow
        #   0656     the other projection, horizontal across the wall
        #   0612     the three of them taking the applause
        "second": ["_DSC0634.jpg", "_MG_0437.jpg", "_DSC0483.jpg",
                   "_MG_0531.jpg", "_DSC0656.jpg", "_DSC0612.jpg"],
    },
]


def from_git(ref):
    out = subprocess.run(["git", "show", ref], capture_output=True, text=True)
    if out.returncode:
        sys.exit("cannot read %s out of git:\n%s" % (ref, out.stderr.strip()))
    return out.stdout


def photos():
    """The filenames, by slug and by folder, from data/archive-photos.txt."""
    out, slug = {}, None
    if not os.path.exists(DATA):
        return out
    for line in open(DATA, encoding="utf-8"):
        raw = line.rstrip("\n")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1] not in (" ", "\t"):
            slug = raw.split("|")[0].strip()
            out[slug] = {}
        elif slug:
            kind, _, name = raw.strip().partition(" ")
            out[slug].setdefault(kind, []).append(name.strip())
    return out


def section(src, pattern):
    m = re.search(pattern, src, re.S)
    return m.group(1).strip() if m else ""


def page(spec, shots):
    src = from_git(spec["source"])
    web = shots.get("web", [])
    raw = shots.get(spec["originals"], [])
    base = "%s/%s" % (CDN, spec["folder"])
    title = html.escape(spec["title"])

    def grid(names, folder, cls, alt):
        return "".join(
            '<a class="{cls}" href="{b}/{f}/{n}" target="_blank" title="{n}">'
            '<img src="{b}/{f}/{n}" alt="{alt}" loading="lazy"></a>'.format(
                cls=cls, b=base, f=folder, n=html.escape(n), alt=alt)
            for n in names)

    chosen = [n for n in spec.get("top", []) if n in web] or web[:4]
    top = "".join(
        '<a class="g-item" href="{b}/web/{n}" target="_blank">'
        '<img src="{b}/web/{n}" alt="{t}"></a>'.format(b=base, n=html.escape(n), t=title)
        for n in chosen)

    second = [n for n in spec.get("second", []) if n in web]
    more = ""
    if second:
        more = ('        <section class="event-gallery">\n'
                '          <div class="g-grid">{items}</div>\n'
                '        </section>\n\n'.format(items="".join(
                    '<a class="g-item" href="{b}/web/{n}" target="_blank" title="{n}">'
                    '<img src="{b}/web/{n}" alt="{t}" loading="lazy"></a>'.format(
                        b=base, n=html.escape(n), t=title)
                    for n in second)))

    originals = ""
    if raw:
        originals = (
            '    <header class="allphotos-modal-head" style="margin-top:32px">\n'
            '      <h2>Originals</h2>\n'
            '      <p>{n} full-resolution JPGs. Click to download.</p>\n'
            '    </header>\n'
            '    <div class="ga-raw-grid">{items}</div>\n'.format(
                n=len(raw),
                items="".join(
                    '<a class="ga-raw-item" href="{b}/{f}/{n}" target="_blank" download>'
                    '<span class="ga-raw-name">{n}</span>'
                    '<span class="ga-raw-ext">{e}</span></a>'.format(
                        b=base, f=spec["originals"], n=html.escape(x),
                        e=x.rsplit(".", 1)[-1].lower())
                    for x in raw)))

    booklet = ""
    if spec.get("booklet") and os.path.exists(spec["booklet"]):
        booklet = ('\n          <a href="../{p}" class="btn">Read the programme '
                   '<span class="ar">&#8594;</span></a>'.format(p=spec["booklet"]))

    description = section(src, r'<section class="event-description">(.*?)</section>')
    # the practical lead belongs to a concert that is coming, not to a record
    description = re.sub(r'<p class="event-lede">.*?</p>', "", description, flags=re.S).strip()
    performers = section(src, r'<ul class="art-list">(.*?)</ul>')
    programme = section(src, r'<ul class="pgm-list">(.*?)</ul>')

    head = from_git(spec["source"])
    head = head[:head.index("</head>")]
    css = re.search(r'href="(\.\./assets/styles\.css\?v=\d+)"', head).group(1)
    js = re.search(r'src="(\.\./assets/site\.js\?v=\d+)"', from_git(spec["source"]))
    js = js.group(1) if js else "../assets/site.js"

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - {year} &#183; CreArtBox</title>
<meta name="description" content="{title} - {month} {day}, {year}. {venue_plain}, {place}. CreArtBox archive.">
<link rel="icon" type="image/svg+xml" href="../brand/mark-wedge-box.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,300..700;1,300..700&family=Literata:ital,opsz,wght@0,7..72,300..700;1,7..72,300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css}">
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
      <div class="nav-item"><a href="../concerts.html">Calendar</a></div>
      <div class="nav-item"><a href="../archive.html" class="active">Archive</a></div>
      <div class="nav-item"><a href="../projects.html">Projects</a></div>
      <div class="nav-item"><a href="../opportunities.html">Opportunities</a></div>
      <div class="nav-item"><a href="../media.html">Media</a></div>
      <div class="nav-item"><a href="../news.html">News</a></div>
      <div class="nav-item"><a href="../support.html">Donate</a></div>
    </div>
  </nav>
</header>

<main>

<section class="event-page">
  <div class="wrap">
    <a href="../archive.html" class="back-to-archive">&#8592; Archive of performances</a>

    <header class="event-header">
      <div class="event-series">Part of: {part_of}</div>
      <h1 class="event-title">{title}</h1>
    </header>

    <section class="event-media"><div class="g-grid" data-count="{topn}">{top}</div></section>

    <div class="event-layout">
      <div class="event-main">
        <section class="event-description">
          {description}
        </section>
        <section class="event-artists">
          <h2 class="event-h2">Performers</h2>
          <ul class="art-list">{performers}</ul>
        </section>

{more}        <section class="event-allphotos">
          <button class="btn allphotos-trigger" id="allphotos-btn">Show all {nweb} photos <span class="ar">&#8594;</span></button>
          <p class="allphotos-hint">Includes the full-resolution originals for download.</p>
        </section>
      </div>
      <aside class="event-sidebar">
        <div class="event-meta">
          <div class="meta-row">
            <div class="meta-h">Date</div>
            <div class="meta-v"><span class="meta-month">{month}</span> <span class="meta-day">{day}</span>, <span class="meta-year">{year}</span></div>
          </div>
          <div class="meta-row">
            <div class="meta-h">Venue</div>
            <div class="meta-v">{venue}<br><span style="font-family:var(--sans);font-size:14px;color:var(--ink-soft);font-weight:400">{place}</span></div>
          </div>
          <div class="meta-row">
            <div class="meta-h">Part of</div>
            <div class="meta-v">{part_of}</div>
          </div>
        </div>
        <section class="event-program">
          <h2 class="event-h2">Program</h2>
          <ul class="pgm-list">{programme}</ul>
        </section>
        <section class="event-funders-logos">
          <div class="pf-label">Supported by</div>
          <div class="pf-logos"><img src="../assets/logos/nyc-cultural-affairs.png" alt="NYC Department of Cultural Affairs"><img src="../assets/logos/nysca.png" alt="New York State Council on the Arts"></div>
        </section>
        <div class="event-foot">
          <a href="../archive.html" class="btn">&#8592; Back to the archive</a>{booklet}
          <a href="../concerts.html" class="btn">See upcoming concerts <span class="ar">&#8594;</span></a>
        </div>
      </aside>
    </div>
  </div>
</section>

</main>

<div class="allphotos-modal" id="allphotos-modal" aria-hidden="true" role="dialog">
  <div class="allphotos-modal-bg" data-allphotos-close></div>
  <div class="allphotos-modal-content">
    <button class="allphotos-modal-close" data-allphotos-close aria-label="Close">&#215;</button>
    <header class="allphotos-modal-head">
      <h2>{title} - all photos</h2>
      <p>{nweb} web-size JPGs (click to open full size, right-click to save).</p>
    </header>
    <div class="ga-grid">{gallery}</div>
{originals}  </div>
</div>

<footer class="colophon">
  <div class="wrap">
    <div class="colophon-grid">
      <div>
        <div class="colophon-mark"><img src="../brand/mark-wedge-amber.svg" alt="CreArtBox" width="52" height="24"></div>
        <p class="colophon-bio">A 501(c)(3) non-profit chamber music ensemble. New York &#183; Asturias.</p>
        <p class="colophon-addr">info@creartbox.nyc &#183; 10&#8211;48 47th Road, Unit 1, Queens, NY 11101</p>
      </div>
      <div><h4>Program</h4><ul><li><a href="../concerts.html">Calendar</a></li><li><a href="../classical-concerts-nyc.html">Coming to a concert</a></li><li><a href="../archive.html">Archive of Performances</a></li><li><a href="../projects.html">Productions</a></li><li><a href="https://festivaladar.com" target="_blank" rel="noopener">Festival ADAR</a></li><li><a href="https://apps.apple.com/us/app/creartbox/id6746415261" target="_blank" rel="noopener">iOS app &#183; App Store</a></li></ul></div>
      <div><h4>The Organization</h4><ul><li><a href="../about.html">About</a></li><li><a href="../presenters.html">For presenters</a></li><li><a href="../news.html">News</a></li><li><a href="../opportunities.html">Opportunities</a></li><li><a href="../brand.html">Brand &amp; press kit</a></li><li><a href="../media.html#magazine">CreArt Magazine</a></li></ul></div>
      <div><h4>Give</h4><ul><li><a href="../support.html">Donate</a></li></ul></div>
    </div>
    <div class="colophon-bot"><span>&#169; CreArtBox, Inc. 2013&#8211;2027 &#183; 501(c)(3) non-profit</span></div>
  </div>
</footer>

<script src="{js}"></script>
</body>
</html>
""".format(title=title, year=spec["year"], month=spec["month"], day=spec["day"],
           venue=spec["venue"], venue_plain=re.sub(r"\s*·.*", "", spec["venue"]),
           place=spec["place"], part_of=html.escape(spec["part_of"]),
           css=css, js=js, top=top, topn=len(chosen),
           description=description, performers=performers, programme=programme,
           nweb=len(web), gallery=grid(web, "web", "ga-item", ""),
           originals=originals, booklet=booklet, more=more)


def sync_cover(spec, src):
    """Point this production's thumbnail in archive.html at `cover`.

    The entry is found by the link it already carries to the gallery
    page, so nothing depends on the order of the file. Until now `cover`
    was written down and read by nobody: the thumbnail had been typed
    into archive.html by hand when the concert was filed, and could sit
    there pointing at a frame the gallery no longer showed.
    """
    url = "%s/%s/web/%s" % (CDN, spec["folder"], spec["cover"])
    link = 'href="archive/%s.html"' % spec["slug"]
    at = src.find(link)
    if at == -1:
        return src, False
    start = src.rfind('<div class="eventpast">', 0, at)
    if start == -1:
        return src, False
    block = src[start:at]
    new = re.sub(r'(<img class="imgpastevents"[^>]*\ssrc=")[^"]*(")',
                 lambda m: m.group(1) + url + m.group(2), block, count=1)
    if new == block:
        return src, False
    return src[:start] + new + src[at:], True


def main():
    check = "--check" in sys.argv
    shots = photos()
    stale = []
    for spec in PAGES:
        if spec["slug"] not in shots:
            print("no photo list for %s in %s" % (spec["slug"], DATA))
            continue
        path = "archive/%s.html" % spec["slug"]
        wanted = page(spec, shots[spec["slug"]])
        try:
            import seo_block
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import seo_block
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if seo_block.strip(current) == wanted:
            continue
        stale.append(path)
        if not check:
            open(path, "w", encoding="utf-8").write(seo_block.carry(current, wanted))

    index = open("archive.html", encoding="utf-8").read()
    out = index
    for spec in PAGES:
        if spec.get("cover"):
            out, _ = sync_cover(spec, out)
    if out != index:
        stale.append("archive.html")
        if not check:
            open("archive.html", "w", encoding="utf-8").write(out)

    if check:
        if stale:
            print("photo page out of date (%d):" % len(stale))
            for p in stale:
                print("  -", p)
            print("\nRun: python3 tools/build_photo_page.py")
            return 1
        print("photo pages are current (%d)" % len(PAGES))
        return 0
    print("wrote %d photo page(s)" % len(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
