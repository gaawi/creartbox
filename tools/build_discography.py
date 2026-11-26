#!/usr/bin/env python3
"""Write discography.html from data/records.json.

    python3 tools/build_discography.py            # write the page
    python3 tools/build_discography.py --check    # fail if it is stale

Three records exist and none of them were anywhere on the site: the
masters, the covers and the tracklists sit in Bunny and nobody outside
the ensemble could hear a note or buy a copy. This builds the page that
fixes that, from the one data file, so the tracklist on the page and the
tracklist beside the masters cannot drift apart.

Audio is the dock that already carries the media page: a single
#featured-tracks container holds every record on the page, so the queue
runs from the first track of the first to the last of the last, and it
keeps playing while the visitor walks around the site.

A record sets "audio": false while its mp3s are not uploaded yet, and
then its tracks print with no play button. Twenty-three buttons that all
404 would be worse than none.
"""

import html
import json
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_block  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = "data/records.json"
PAGE = "discography.html"

TITLE = "Recordings - CreArtBox &#183; Discography"

WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}


def count_word(n):
    return WORDS.get(n, str(n))


def describe(recs):
    """The meta description, from whatever records are on the page.

    It used to name all three by hand, which went stale the moment two
    of them came off.
    """
    if not recs:
        return "CreArtBox recordings."
    tail = ("Listen in full, streamed as the uncompressed master, or order a "
            "signed CD or LP.")
    if len(recs) == 1:
        r = recs[0]
        return "The record CreArtBox has made: %s, %s. %s" % (
            esc(r["title"]), esc(r["composerLine"]), tail)
    names = [esc(r["title"]) for r in recs]
    which = ", ".join(names[:-1]) + " and " + names[-1]
    return "The %s records CreArtBox has made: %s. %s" % (
        count_word(len(recs)).lower(), which, tail)


def esc(text):
    return html.escape(text, quote=True).replace("&#x27;", "&#x27;")


def money(n):
    return "$%d" % n


def order_link(rec, fmt, price, to):
    """A mailto that already knows which record and which format."""
    subject = "RECORD ORDER %s %s" % (fmt.upper(), rec["title"])
    body = (
        "I would like to order the %s of %s.\n\n"
        "Format: %s (%s plus shipping)\n"
        "Copies: 1\n"
        "Name:\n"
        "Shipping address:\n\n"
        "Who should the note be made out to?\n"
    ) % (fmt, rec["title"], fmt, money(price))
    return "mailto:%s?subject=%s&body=%s" % (to, quote(subject), quote(body))


def megabytes(n):
    if n >= 1000 * 1000 * 1000:
        return "%.1f GB" % (n / 1000.0 ** 3)
    return "%d MB" % round(n / 1000.0 ** 2)


def track_rows(rec, base=None):
    out = []
    for t in rec["tracks"]:
        title = t["work"]
        note = t["movement"]
        # Noctum is twelve numbers from one work, so the work's name is
        # the record's name and printing it on every line says nothing.
        if title == rec["title"] and note:
            title, note = note, ""
        line = esc(title)
        if note:
            line += ' <span class="track-note">%s</span>' % esc(note)
        num = "%02d" % t["n"]
        size = megabytes(t["bytes"])
        if rec.get("audio") and t.get("url"):
            # the separator is an entity and must not be escaped again
            label = " &#183; ".join(esc(x) for x in (title, note) if x)
            attrs = (' class="track" data-track-src="%s" data-track-composer="%s"'
                     ' data-track-title="%s" data-track-note="%s"'
                     % (esc(t["url"]), esc(t["composer"]), label,
                        esc("%s, %s" % (rec["format"], size))))
            button = ('<button type="button" class="track-play" aria-label="Play">'
                      '<span class="tp-glyph" aria-hidden="true"></span></button>')
        else:
            attrs = ' class="track is-quiet"'
            button = '<span class="track-num-only">%s</span>' % num
        out.append(
            '          <li%s>\n'
            '            %s\n'
            '            <div class="track-meta"><div class="track-composer">%s</div>'
            '<div class="track-title">%s</div></div>\n'
            '            <span class="track-dur">%s<span class="track-mb">%s</span></span>\n'
            '          </li>'
            % (attrs, button, esc(t["composer"]), line, esc(t["duration"]), esc(size)))
    return "\n".join(out)


def record_block(rec, data):
    p = data["prices"]
    to = data["orderTo"]
    facts = []
    if rec.get("performers"):
        facts.append(("Played by", esc(rec["performers"])))
    if rec.get("engineer"):
        facts.append(("Sound", esc(rec["engineer"])))
    facts.append(("Running time", esc(rec["totalTime"]) + " &#183; %d tracks" % len(rec["tracks"])))
    facts.append(("Streaming", esc(rec["format"]) + ", the master itself &#183; "
                  + esc(megabytes(rec["bytes"])) + " in all"))
    fact_rows = "".join(
        '<li><span class="rec-f-h">%s</span><span class="rec-f-v">%s</span></li>' % (h, v)
        for h, v in facts)

    notes = [rec.get("recordedNote", ""), rec.get("sourceNote", "")]
    recorded = "".join('\n        <p class="rec-note">%s</p>' % esc(n) for n in notes if n)

    vinyl_note = ""
    if rec.get("vinylNote"):
        vinyl_note = '\n          <p class="rec-vinyl-note">%s</p>' % rec["vinylNote"]

    quiet = ""
    if not rec.get("audio"):
        quiet = ('\n        <p class="rec-quiet">The recording is being prepared '
                 'for streaming. Write to us and we will tell you when it is up.</p>')

    return (
        '    <article class="rec" id="{slug}">\n'
        '      <div class="rec-cover">\n'
        '        <img src="assets/img/records/{slug}-600.jpg" width="600" height="600"\n'
        '             alt="Cover of {title}" loading="lazy">\n'
        '        <span class="rec-tag">{tag}</span>\n'
        '      </div>\n'
        '      <div class="rec-body">\n'
        '        <h3 class="rec-t">{title}</h3>\n'
        '        <p class="rec-sub">{sub}</p>\n'
        '        <ul class="rec-facts">{facts}</ul>{recorded}{quiet}\n'
        '        <ol class="track-list">\n'
        '{tracks}\n'
        '        </ol>\n'
        '        <div class="rec-buy">\n'
        '          <a class="btn btn-stamp" href="{cd}" data-cb-track="record_order"\n'
        '             data-cb-record="{slug}" data-cb-format="cd">CD {cdp} '
        '<span class="ar">&#8594;</span></a>\n'
        '          <a class="btn btn-s" href="{lp}" data-cb-track="record_order"\n'
        '             data-cb-record="{slug}" data-cb-format="vinyl">Vinyl {lpp}</a>\n'
        '          <span class="rec-buy-note">Signed, with a personal note. Plus shipping.</span>'
        '{vinyl}\n'
        '        </div>\n'
        '      </div>\n'
        '    </article>\n'
    ).format(slug=esc(rec["slug"]), title=esc(rec["title"]),
             sub=esc(rec["composerLine"]), tag=esc(rec.get("coverTag", "")),
             facts=fact_rows, recorded=recorded, quiet=quiet,
             tracks=track_rows(rec),
             cd=esc(order_link(rec, "CD", p["cd"], to)), cdp=money(p["cd"]),
             lp=esc(order_link(rec, "vinyl", p["vinyl"], to)), lpp=money(p["vinyl"]),
             vinyl=vinyl_note)


def page(data):
    recs = data["records"]
    p = data["prices"]
    blocks = "\n".join(record_block(r, data) for r in recs)
    total_tracks = sum(len(r["tracks"]) for r in recs)
    sizes = [t["bytes"] for r in recs for t in r["tracks"] if t.get("bytes")]
    return TEMPLATE.format(
        title=TITLE, desc=describe(recs), blocks=blocks,
        countw=count_word(len(recs)),
        noun="record" if len(recs) == 1 else "records",
        thisrec=("The record is" if len(recs) == 1 else "Every record is"),
        small=megabytes(min(sizes)) if sizes else "15 MB",
        big=megabytes(max(sizes)) if sizes else "350 MB",
        tracks=total_tracks,
        cd=money(p["cd"]), lp=money(p["vinyl"]),
        order=esc(data["orderTo"]))


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/svg+xml" href="brand/mark-wedge-box.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,300..700;1,300..700&family=Literata:ital,opsz,wght@0,7..72,300..700;1,7..72,300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/styles.css?v=196">
<script id="cb-theme-init">document.documentElement.setAttribute("data-theme","dark");</script>
</head>
<body>

<header class="masthead">
  <div class="masthead-inner">
    <div class="masthead-left"><button class="nav-burger" aria-label="Menu">Menu</button><span class="established">Established 2013, New York City</span></div>
    <a class="masthead-title" href="index.html"><img class="logo-img" src="brand/logo-creartbox-reversed.svg" alt="CreArtBox"></a>
    <div class="masthead-right"><a class="masthead-tickets" href="concerts.html">Get tickets</a></div>
  </div>
  <nav class="nav-strip">
      <div class="nav-strip-inner">
        <div class="nav-item"><a href="index.html">Home</a></div>
        <div class="nav-item">
          <a href="about.html">About</a>
          <div class="submenu">
            <a href="about.html#bio">Biography</a>
            <a href="ensemble.html">The Ensemble</a>
            <a href="composers.html">Composers</a>
            <a href="staff.html">Staff & Collaborators</a>
            <a href="supporters.html">Supporters</a>
          </div>
        </div>
        <div class="nav-item">
          <a href="concerts.html">Calendar</a>
          <div class="submenu">
            <a href="concerts.html">Upcoming concerts</a>
            <a href="concerts.html#nys">New York Series</a>
            <a href="concerts.html">Touring</a>
            <a href="https://festivaladar.com" target="_blank" rel="noopener">Festival ADAR</a>
          </div>
        </div>
        <div class="nav-item">
          <a href="archive.html">Archive</a>
          <div class="submenu">
            <a href="archive.html#y2026">2026 &#8211; 2025</a>
            <a href="archive.html#y2024">2024 &#8211; 2022</a>
            <a href="archive.html#y2021">2021 &#8211; 2018</a>
            <a href="archive.html#y2017">Before 2018</a>
          </div>
        </div>
        <div class="nav-item">
          <a href="projects.html">Projects</a>
          <div class="submenu">
            <a href="projects.html#visual-concerts">Visual concerts</a>
            <a href="projects.html#staged">Staged productions</a>
            <a href="projects.html#outreach">Outreach &amp; education</a>
            <a href="projects.html#digital">Digital &amp; experimental</a>
            <a href="projects.html#adar">Festival ADAR</a>
          </div>
        </div>
        <div class="nav-item">
          <a href="opportunities.html">Opportunities</a>
          <div class="submenu">
            <a href="opportunities.html#composer-in-residence">Composer-in-Residence</a>
            <a href="opportunities.html#scores-international">Call for Scores &#183; International</a>
            <a href="opportunities.html#scores-american">Call for Scores &#183; American</a>
            <a href="opportunities.html#visual-artists">Call for Visual Artists</a>
          </div>
        </div>
        <div class="nav-item">
          <a href="media.html" class="active">Media</a>
          <div class="submenu">
            <a href="media.html#videos">Videos</a>
            <a href="media.html#audio">Audio</a>
            <a href="discography.html">Recordings</a>
            <a href="media.html#photos">Photographs</a>
            <a href="media.html#magazine">CreArt Magazine</a>
            <a href="media.html#podcast">Live Podcast</a>
            <a href="media.html#social">Social</a>
            <a href="https://apps.apple.com/us/app/creartbox/id6746415261" target="_blank" rel="noopener">iOS app</a>
          </div>
        </div>
        <div class="nav-item">
          <a href="news.html">News</a>
        </div>
        <div class="nav-item">
          <a href="support.html">Donate</a>
          <div class="submenu">
            <a href="support.html">Donate</a>
            <a href="support.html#sponsor">Sponsorship</a>
            <a href="support.html">Mail a check</a>
          </div>
        </div>
      </div>
    </nav>
</header>

<main>

<!-- ============ DISCOGRAPHY ============ -->
<section class="section" id="records">
  <div class="wrap">
    <div class="two-col">
      <div>
        <span class="label">Discography &#183; lossless</span>
        <h2 class="h-title" style="margin-top:14px">The <em>{noun}</em>.</h2>
      </div>
      <div>
        <p class="body">{countw} {noun}, {tracks} tracks, and what plays here is the
        master: the uncompressed studio file, note for note, not a copy squeezed
        down for streaming. Give it a moment to load. The player then follows you
        around the site, so you can start something here and keep listening while
        you read something else.</p>
        <p class="body" style="margin-top:14px">A track is between {small} and {big},
        which is the price of hearing it properly. Each one says its size below.
        On a phone, wait for Wi-Fi.</p>
        <p class="body" style="margin-top:14px">{thisrec} also a physical object:
        a CD at {cd} and a vinyl LP at {lp}, signed, and sent with a
        personal note from the artists. Shipping is charged on top and depends on
        where you are. Orders and questions go to
        <a href="mailto:{order}">{order}</a>.</p>
      </div>
    </div>
  </div>
</section>

<section class="section tinted" style="padding-top:0;padding-bottom:64px;border-top:0">
  <div class="wrap">
    <div id="featured-tracks">
{blocks}
    </div>
  </div>
</section>

</main>

<footer class="colophon">
  <div class="wrap">
    <div class="colophon-grid">
      <div>
        <div class="colophon-mark"><img src="brand/mark-wedge-amber.svg" alt="CreArtBox" width="52" height="24"></div>
        <p class="colophon-bio">A 501(c)(3) non-profit chamber music ensemble. Creating and producing live art performances that fuse classical and contemporary music with visual art and design. New York &#183; Asturias.</p>
        <p class="colophon-addr">info@creartbox.nyc &#183; 10&#8211;48 47th Road, Unit 1, Queens, NY 11101</p>
        <div class="colophon-social">
          <a href="https://www.instagram.com/creartboxnyc/" target="_blank" rel="noopener">Instagram</a>
          <a href="https://www.youtube.com/creartbox" target="_blank" rel="noopener">YouTube</a>
          <a href="https://www.facebook.com/creartbox" target="_blank" rel="noopener">Facebook</a>
          <a href="https://www.tiktok.com/@creartbox" target="_blank" rel="noopener">TikTok</a>
          <a href="https://x.com/creartbox" target="_blank" rel="noopener">X</a>
        </div>
      </div>
      <div><h4>Program</h4><ul><li><a href="concerts.html">Calendar</a></li><li><a href="discography.html">Recordings</a></li><li><a href="lottery.html">Free tickets</a></li><li><a href="classical-concerts-nyc.html">Coming to a concert</a></li><li><a href="archive.html">Archive of Performances</a></li><li><a href="projects.html">Productions</a></li><li><a href="https://digitalconcerthall.vercel.app/" target="_blank" rel="noopener">play.creartbox.nyc</a></li><li><a href="https://festivaladar.com" target="_blank" rel="noopener">Festival ADAR</a></li><li><a href="https://apps.apple.com/us/app/creartbox/id6746415261" target="_blank" rel="noopener">iOS app &#183; App Store</a></li></ul></div>
      <div><h4>The Organization</h4><ul><li><a href="about.html">About</a></li><li><a href="news.html">News</a></li><li><a href="presenters.html">For presenters</a></li><li><a href="ensemble.html">The ensemble</a></li><li><a href="opportunities.html">Opportunities</a></li><li><a href="brand.html">Brand &amp; press kit</a></li><li><a href="media.html#magazine">CreArt Magazine</a></li></ul></div>
      <div><h4>Give</h4><ul><li><a href="support.html">Donate</a></li><li><a href="support.html#sponsor">Sponsorship</a></li></ul></div>
    </div>
    <div class="colophon-bot"><span>&#169; CreArtBox, Inc. 2013&#8211;2026 &#183; A 501(c)(3) non-profit organization</span></div>
  </div>
</footer>

<script src="assets/site.js?v=63"></script>
<div class="audio-dock" id="audio-dock" hidden aria-label="Audio player">
  <div class="ad-info">
    <div class="ad-composer" data-ad-composer>&#8212;</div>
    <div class="ad-title" data-ad-title>Select a track</div>
  </div>
  <div class="ad-controls">
    <button type="button" class="ad-btn" data-ad-prev aria-label="Previous track">&#10229;</button>
    <button type="button" class="ad-btn ad-play" data-ad-play aria-label="Play / pause"><span class="ad-glyph"></span></button>
    <button type="button" class="ad-btn" data-ad-next aria-label="Next track">&#10230;</button>
  </div>
  <div class="ad-progress" data-ad-progress>
    <div class="ad-bar"><div class="ad-fill" data-ad-fill></div></div>
    <div class="ad-time"><span data-ad-t-cur>0:00</span> <span data-ad-t-dur>0:00</span></div>
  </div>
  <button type="button" class="ad-close" data-ad-close aria-label="Close player">&#215;</button>
</div>
</body>
</html>
"""


def main():
    check = "--check" in sys.argv
    os.chdir(ROOT)
    data = json.load(open(DATA, encoding="utf-8"))
    fresh = page(data)
    old = open(PAGE, encoding="utf-8").read() if os.path.exists(PAGE) else ""
    # the SEO block and the version stamps belong to other generators
    fresh = seo_block.carry(old, fresh)
    for pattern in (r'styles\.css\?v=\d+', r'site\.js\?v=\d+'):
        m = re.search(pattern, old)
        if m:
            fresh = re.sub(pattern, m.group(0), fresh)

    if fresh == old:
        print("the discography page is current (%d record(s))" % len(data["records"]))
        return 0
    if check:
        print("discography.html is out of date\n\nRun: python3 tools/build_discography.py")
        return 1
    open(PAGE, "w", encoding="utf-8").write(fresh)
    print("wrote %s: %d record(s), %d track(s)"
          % (PAGE, len(data["records"]),
             sum(len(r["tracks"]) for r in data["records"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
