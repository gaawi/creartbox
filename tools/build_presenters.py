#!/usr/bin/env python3
"""Build the presenters page and the repertoire list.

    python3 tools/build_presenters.py            # write presenters.html, repertoire.html
    python3 tools/build_presenters.py --check    # fail if out of date

Programmes on offer are declared in PROGRAMS below: a title, a
paragraph, and the works with their durations. "Intermission" is a work
with no composer and no duration.

The repertoire page is built from data/repertoire.txt, one work per
line as "Composer - Title". It groups by composer, sorted by surname,
and the page filters as you type.
"""

import html
import os
import re
import sys
import unicodedata

SITE = "https://creartbox.nyc"
CSS = "assets/styles.css?v=134"
JS = "assets/site.js?v=44"
REPERTOIRE = "data/repertoire.txt"
CONTACT = "info@creartbox.nyc"

PROGRAMS = [
    {
        "n": "Program 1",
        "title": "Dvořák and the Schumanns",
        "blurb": (
            "Warmth, lyricism, and rhythmic vitality bring together the music of Dvořák "
            "and the Schumanns. A flute arrangement of Dvořák&#x27;s beloved &quot;American&quot; "
            "Quartet lends a fresh colour to its expansive melodies and spirited exchanges, "
            "before Robert Schumann&#x27;s Piano Quartet draws us into a world of tenderness and "
            "Romantic intensity. After the intermission, Clara Schumann&#x27;s Three Romances "
            "offer a moment of intimate reflection. Dvořák&#x27;s Piano Quintet No. 2 brings the "
            "evening to an exuberant close, balancing songful expression with the irresistible "
            "energy of dance."),
        "works": [
            ("Antonín Dvořák", "String Quartet No. 12 in F major, Op. 96, &quot;American&quot; "
                               "(arrangement with flute)", 24),
            ("Robert Schumann", "Piano Quartet in E-flat major, Op. 47", 25),
            (None, "Intermission", None),
            ("Clara Schumann", "Three Romances, Op. 22", 9),
            ("Antonín Dvořák", "Piano Quintet No. 2 in A major, Op. 81", 40),
        ],
    },
    {
        "n": "Program 2",
        "title": "Ravel, Kurtág, Ligeti, Stravinsky",
        "blurb": (
            "Ravel&#x27;s luminous sound world meets the bold imagination of Hungarian composers "
            "György Kurtág and György Ligeti in a first half shaped by contrast and discovery. "
            "The delicate fairy-tale scenes of <em>Ma mère l&#x27;Oye</em> sit alongside the "
            "concentrated gestures of Kurtág&#x27;s <em>Tre pezzi</em> and the rhythmic wit of "
            "Ligeti&#x27;s <em>Musica ricercata</em>, creating a dialogue between French colour "
            "and Hungarian invention. Ravel&#x27;s <em>Kaddish</em> offers an expressive moment "
            "of contemplation before the intermission. Stravinsky&#x27;s <em>Petrushka</em> then "
            "opens the door to a vivid carnival world, bringing the evening to a close with "
            "bustling dances, theatrical drama, and dazzling musical contrasts."),
        "works": [
            ("Maurice Ravel", "<em>Ma mère l&#x27;Oye</em>", 16),
            ("György Kurtág", "<em>Tre pezzi</em>", 7),
            ("György Ligeti", "<em>Musica ricercata</em>", 15),
            ("Maurice Ravel", "<em>Kaddish</em>", 5),
            (None, "Intermission", None),
            ("Igor Stravinsky", "<em>Petrushka</em>", 40),
        ],
    },
]

ABOUT = [
    "CreArtBox is a New York City-based chamber music ensemble founded in 2013 by flutist "
    "Guillermo Laporta and pianist Josefina Urraca, together with core members Emilie-Anne "
    "Gendron (violin), Matthew Cohen (viola), and Julia Yang (cello). Now in its twelfth "
    "season, the ensemble performs regularly in New York City and tours nationally and "
    "internationally, with appearances across the United States, Spain, Europe, and Japan.",

    "CreArtBox has earned recognition from major arts publications: <em>The New Yorker</em> "
    "named the ensemble among its art and music top picks, and <em>BroadwayWorld</em> "
    "described its performances as &quot;wholly authentic, visually and aurally compelling.&quot; "
    "The ensemble&#x27;s work has been supported by grants and awards from the New York State "
    "Council on the Arts, the New York City Department of Cultural Affairs, and the Amphion "
    "Foundation, among other funders.",

    "Since its founding season, CreArtBox has run an open Call for Scores, through which it "
    "has premiered works by Pulitzer Prize-winning composers alongside emerging voices, and "
    "mentored composers early in their careers.",

    "Guillermo Laporta (flute) is a Spanish flutist, composer, and designer, and Artistic "
    "Director of CreArtBox and Festival ADAR. Josefina Urraca (piano) is a Spanish pianist "
    "and student of Dmitri Bashkirov, whose playing exemplifies &quot;introspection and "
    "musical abandon.&quot; Violinist Emilie-Anne Gendron has been lauded by <em>The Strad</em> "
    "for her &quot;marvelous and lyrical playing&quot; and appears with major orchestras and "
    "ensembles. Violist Matthew Cohen, a special prize winner at the Primrose International "
    "Viola Competition, is described as one of the most sought-after violists of his "
    "generation. Cellist Julia Yang, praised for &quot;her sense of joyful virtuosity,&quot; is "
    "a founding member of the Naumburg-winning Merz Trio. Beyond its core chamber programs, "
    "CreArtBox also produces larger-scale productions and co-produces Festival ADAR, an "
    "international arts festival held in rural Asturias, Spain.",
]

# surnames the last word does not give
PLAYERS = [
    ("Guillermo Laporta", "Flute", "guillermo-laporta", "assets/img/guillermo-laporta.png"),
    ("Josefina Urraca", "Piano", "josefina-urraca", "assets/img/josefina-urraca.png"),
    ("Emilie-Anne Gendron", "Violin", "emilie-anne-gendron", "assets/img/emilie-gendron.webp"),
    ("Matthew Cohen", "Viola", "matthew-cohen", "assets/img/matthew-cohen.jpg"),
    ("Julia Yang", "Cello", "julia-yang", "assets/img/julia-yang.jpg"),
]

PHOTOS = [
    ("creartbox-ensemble.jpg", "The ensemble", "Photo: Tao Ho", "3000 &#215; 1949"),
    ("creartbox-currents-dimenna.jpg", "At The DiMenna Center", "New York Series", "3000 &#215; 2001"),
    ("creartbox-in-performance.jpg", "In performance", "", "2400 &#215; 1600"),
    ("creartbox-fragile-form.jpg", "The Fragile Form Trilogy", "2022", "3000 &#215; 1605"),
    ("creartbox-festival-adar.jpg", "Festival ADAR", "Asturias", "1600 &#215; 941"),
]

DOSSIER = "downloads/creartbox-program-dossier.pdf"

FACTS = [
    ("Ensemble", "Piano quintet: flute, piano, violin, viola and cello"),
    ("Smaller formations", "Duo, trio and quartet from the same players"),
    ("Programme length", "Two halves with one intermission, adaptable"),
    ("Fees", "On request, by formation and date"),
    ("Based", "New York City, touring from there"),
]

SORT = {
    "Carl Maria von Weber": "Weber",
    "Ludwig van Beethoven": "Beethoven",
    "Manuel de Falla": "Falla",
    "Mario Díaz de León": "Diaz de Leon",
    "Michel van der Aa": "Aa",
    "Zygmund de Somogyi": "Somogyi",
    "Eli Tausen á Lava": "Tausen a Lava",
    "Jacob TV": "TV",
    "JP Jofre": "Jofre",
    "Yurui (Rain)": "Yurui",
    "Dai Wei": "Dai Wei",
    "Sam Wu": "Wu",
    "Seong Ae Kim": "Kim",
    "Evan O. Adams": "Adams",
    "Marcos Fernández and Ander García": "Fernandez",
}


def plain(text):
    """Sortable: no accents, no case."""
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn").lower()


def surname(composer):
    return plain(SORT.get(composer, composer.split()[-1]))


# ------------------------------------------------------------- repertoire

def repertoire():
    """[(composer, [work, ...]), ...] by surname."""
    by_composer = {}
    for line in open(REPERTOIRE, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        composer, _, work = line.partition(" — ")
        if not work:
            raise SystemExit("  !! no separator in: " + line)
        by_composer.setdefault(composer.strip(), []).append(work.strip())
    return sorted(by_composer.items(), key=lambda kv: (surname(kv[0]), plain(kv[0])))


# ------------------------------------------------------------------ pieces

def head(title, description, canonical, extra=""):
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{site}/assets/img/ensemble.jpg">
<link rel="icon" type="image/svg+xml" href="brand/mark-wedge-box.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,300..700;1,300..700&family=Literata:ital,opsz,wght@0,7..72,300..700;1,7..72,300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css}">
<script id="cb-theme-init">document.documentElement.setAttribute("data-theme","dark");</script>
{extra}</head>
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
      <div class="nav-item"><a href="about.html">About</a></div>
      <div class="nav-item"><a href="concerts.html">Calendar</a></div>
      <div class="nav-item"><a href="archive.html">Archive</a></div>
      <div class="nav-item"><a href="projects.html">Projects</a></div>
      <div class="nav-item"><a href="opportunities.html">Opportunities</a></div>
      <div class="nav-item"><a href="media.html">Media</a></div>
      <div class="nav-item"><a href="news.html">News</a></div>
      <div class="nav-item"><a href="support.html">Donate</a></div>
    </div>
  </nav>
</header>

<main>
""".format(title=html.escape(title, quote=True),
           description=html.escape(description, quote=True),
           canonical=canonical, css=CSS, site=SITE, extra=extra,
           )


def foot():
    return """
</main>

<footer class="colophon">
  <div class="wrap">
    <div class="colophon-grid">
      <div>
        <div class="colophon-mark"><img src="brand/mark-wedge-amber.svg" alt="CreArtBox" width="52" height="24"></div>
        <p class="colophon-bio">A 501(c)(3) non-profit chamber music and multimedia ensemble. New York &#183; Asturias.</p>
        <p class="colophon-addr">info@creartbox.nyc &#183; 10&#8211;48 47th Road, Unit 1, Queens, NY 11101</p>
        <div class="colophon-social">
          <a href="https://www.instagram.com/creartboxnyc/" target="_blank" rel="noopener">Instagram</a>
          <a href="https://www.youtube.com/creartbox" target="_blank" rel="noopener">YouTube</a>
          <a href="https://www.facebook.com/creartbox" target="_blank" rel="noopener">Facebook</a>
          <a href="https://www.tiktok.com/@creartbox" target="_blank" rel="noopener">TikTok</a>
          <a href="https://x.com/creartbox" target="_blank" rel="noopener">X</a>
        </div>
      </div>
      <div><h4>Program</h4><ul><li><a href="concerts.html">Calendar</a></li><li><a href="archive.html">Archive of Performances</a></li><li><a href="projects.html">Productions</a></li><li><a href="https://festivaladar.com" target="_blank" rel="noopener">Festival ADAR</a></li><li><a href="https://apps.apple.com/us/app/creartbox/id6746415261" target="_blank" rel="noopener">iOS app &#183; App Store</a></li></ul></div>
      <div><h4>The Organization</h4><ul><li><a href="about.html">About</a></li><li><a href="news.html">News</a></li><li><a href="presenters.html">For presenters</a></li><li><a href="opportunities.html">Opportunities</a></li><li><a href="brand.html">Brand &amp; press kit</a></li></ul></div>
      <div><h4>Give</h4><ul><li><a href="support.html">Donate</a></li></ul></div>
    </div>
    <div class="colophon-bot"><span>&#169; CreArtBox, Inc. 2013&#8211;2027 &#183; 501(c)(3) non-profit</span></div>
  </div>
</footer>

<script src="{js}"></script>
</body>
</html>
""".format(js=JS)


def program_block(program):
    rows, total = [], 0
    for composer, work, mins in program["works"]:
        if composer is None:
            rows.append('        <li class="pgm-break"><span>{}</span></li>'.format(work))
            continue
        total += mins
        rows.append(
            '        <li><span class="pgm-composer">{c}</span>'
            '<span class="pgm-work">{w} <span class="pgm-mins">{m}&#x27;</span></span></li>'.format(
                c=composer, w=work, m=mins))
    return ("""    <article class="offer">
      <div class="offer-head">
        <span class="label">{n}</span>
        <h3 class="offer-title">{title}</h3>
      </div>
      <div class="offer-body">
        <p class="body-l">{blurb}</p>
        <ul class="pgm-list offer-list">
{rows}
        </ul>
        <p class="offer-total">Music, about {total} minutes, with one intermission.</p>
      </div>
    </article>""".format(n=program["n"], title=html.escape(program["title"], quote=True),
                         blurb=program["blurb"], rows="\n".join(rows), total=total))


# ------------------------------------------------------------------- pages

def facts_block():
    rows = "".join(
        '        <div class="pres-fact"><dt>{k}</dt><dd>{v}</dd></div>\n'.format(k=k, v=v)
        for k, v in FACTS)
    return '      <dl class="pres-facts">\n{}      </dl>'.format(rows)


def roster_block():
    cards = []
    for name, role, slug, photo in PLAYERS:
        cards.append(
            '        <a class="pres-player" href="artists/{slug}.html">\n'
            '          <span class="pres-portrait"><img src="{photo}" alt="{name}, {low}" loading="lazy"></span>\n'
            '          <span class="pres-player-name">{name}</span>\n'
            '          <span class="pres-player-role">{role}</span>\n'
            '          <span class="pres-player-more">Biography <span class="ar">&#8594;</span></span>\n'
            '        </a>'.format(slug=slug, photo=photo, name=name, role=role,
                                  low=role.lower()))
    return "\n".join(cards)


def photos_block():
    shots = []
    for filename, title, note, size in PHOTOS:
        shots.append(
            '        <a class="pres-shot" href="assets/press/photos/{f}" download>\n'
            '          <img src="assets/press/photos/t-{f}" alt="{t}" loading="lazy">\n'
            '          <span class="pres-shot-cap">{t}<span>{note}JPEG &#183; {size}</span></span>\n'
            '        </a>'.format(f=filename, t=title, size=size,
                                  note=(note + " &#183; ") if note else ""))
    return "\n".join(shots)


def booking_page():
    programs = "\n".join(program_block(p) for p in PROGRAMS)
    about = "\n      ".join("<p>%s</p>" % p for p in ABOUT)
    return (head("For presenters &#183; CreArtBox",
                 "Programmes on offer, the players, materials to download, and "
                 "who to write to about a date and a fee.",
                 SITE + "/presenters.html")
            + """
<section class="pres-top">
  <div class="wrap">
    <div class="pres-print-head">
      <img class="pres-print-mark" src="brand/logo-creartbox-black.svg" alt="CreArtBox">
      <div class="pres-print-title">
        <strong>Concert programme dossier</strong>
        <span>2026 / 27 &#183; twelfth season &#183; info@creartbox.nyc &#183; creartbox.nyc</span>
      </div>
    </div>

    <div class="page-folio-head">
      <span class="label">For presenters</span>
      <hr class="rule" style="width:100%">
      <span class="label ital">Programmes, players and materials</span>
    </div>
    <h1 class="sr-only">For presenters</h1>

{facts}

    <div class="pres-actions">
      <a class="btn btn-stamp" href="mailto:{contact}?subject=Booking%20enquiry">Enquire about a date <span class="ar">&#8594;</span></a>
      <a class="btn" href="{dossier}" download>Programme dossier &#183; PDF</a>
      <a class="btn" href="repertoire.html">Full repertoire</a>
    </div>
  </div>
</section>

<section class="section pres-programs">
  <div class="wrap">
    <div class="section-title">
      <hr class="rule">
      <div class="head"><span class="label">On offer</span><span class="bar"></span><span class="label ital">Two <em>programmes</em>.</span></div>
      <hr class="rule">
    </div>

{programs}

    <p class="offer-note">Both programmes can be adapted to suit different concert lengths, and
      either can be played by a smaller group: a piano trio, a flute, cello and piano trio, or
      a duo. This season the ensemble tours a piano trio to Illinois and a flute, cello and
      piano programme to the Hudson Valley. For a programme built around a theme, an
      anniversary or a local commission, write to <a href="mailto:{contact}">{contact}</a>:
      the ensemble has played <a href="repertoire.html">everything listed here</a>, and reads
      new scores every season through its open call. Fees on request.</p>
  </div>
</section>

<section class="section tinted pres-roster-wrap">
  <div class="wrap">
    <div class="section-title">
      <hr class="rule">
      <div class="head"><span class="label">The players</span><span class="bar"></span><span class="label ital">Biographies, <em>as they wrote them</em>.</span></div>
      <hr class="rule">
    </div>
    <div class="pres-roster">
{roster}
    </div>
    <p class="offer-note">Each biography is published in three lengths, with a character
      count, and may be reproduced without alteration. The ensemble biography is on the
      <a href="about.html#bio">about page</a>, also in three lengths.</p>
  </div>
</section>

<section class="section pres-materials">
  <div class="wrap">
    <div class="section-title">
      <hr class="rule">
      <div class="head"><span class="label">Materials</span><span class="bar"></span><span class="label ital">Ready to <em>download</em>.</span></div>
      <hr class="rule">
    </div>

    <div class="pres-files">
      <div>
        <h3 class="offer-title">Documents</h3>
        <ul class="pres-dl">
          <li><a href="{dossier}" download>Programme dossier <span>PDF</span></a></li>
          <li><a href="downloads/creartbox-season-2026-27.pdf" download>Season press release <span>PDF</span></a></li>
          <li><a href="assets/press/creartbox-bio-short.pdf" download>Ensemble biography, short <span>PDF</span></a></li>
          <li><a href="assets/press/creartbox-bio-medium.pdf" download>Ensemble biography, medium <span>PDF</span></a></li>
          <li><a href="assets/press/creartbox-bio-long.pdf" download>Ensemble biography, long <span>PDF</span></a></li>
          <li><a href="downloads/currents-2026-program.pdf" download>A printed programme, as an example <span>PDF</span></a></li>
        </ul>
      </div>
      <div>
        <h3 class="offer-title">Logos and brand</h3>
        <ul class="pres-dl">
          <li><a href="downloads/creartbox-brand-assets.zip" download>All brand assets <span>ZIP</span></a></li>
          <li><a href="brand/logo-creartbox-reversed.svg" download>Wordmark, reversed <span>SVG</span></a></li>
          <li><a href="brand/logo-creartbox-black.svg" download>Wordmark, black <span>SVG</span></a></li>
          <li><a href="brand.html">The full press kit <span>page</span></a></li>
        </ul>
      </div>
    </div>

    <h3 class="offer-title pres-photos-h">Photographs</h3>
    <div class="pres-shots">
{photos}
    </div>
    <p class="pres-dl-all"><a class="btn btn-stamp btn-s" href="downloads/creartbox-press-photos.zip" download>All photographs &#183; ZIP, 2.2&#8201;MB</a>
      <span>Free to use for concert promotion, with the credit given under each file.</span></p>
  </div>
</section>

<section class="section tinted pres-about">
  <div class="wrap">
    <div class="section-title">
      <hr class="rule">
      <div class="head"><span class="label">The ensemble</span><span class="bar"></span><span class="label ital">About <em>CreArtBox</em>.</span></div>
      <hr class="rule">
    </div>
    <div class="offer-about">
      <figure>
        <div class="imedia"><img src="assets/img/ensemble.jpg" alt="The CreArtBox ensemble" loading="lazy"></div>
        <figcaption class="cap">CreArtBox ensemble &#183; Photo: Tao Ho</figcaption>
      </figure>
      <div class="offer-about-text">
      {about}
      </div>
    </div>
  </div>
</section>

<section class="section pres-contact-wrap">
  <div class="wrap">
    <div class="pres-contact">
      <div>
        <span class="label">Bookings</span>
        <p>Guillermo Laporta and Josefina Urraca, directors<br>
          <a href="mailto:{contact}">{contact}</a><br>
          CreArtBox, Inc. &#183; 10&#8211;48 47th Road, Unit 1, Queens, NY 11101</p>
      </div>
      <div>
        <span class="label">What to tell us</span>
        <p>The date, the hall and its instrument, the length of concert, and whether you
          want the quintet or a smaller formation. We answer with availability and a fee.</p>
      </div>
    </div>
  </div>
</section>
""".format(programs=programs, about=about, contact=CONTACT, facts=facts_block(),
           roster=roster_block(), photos=photos_block(), dossier=DOSSIER)
            + foot())


def repertoire_page():
    groups = repertoire()
    works = sum(len(w) for _, w in groups)
    blocks = []
    for composer, titles in groups:
        items = "\n".join(
            '          <li class="rep-work" data-rep="{key}">{title}</li>'.format(
                key=html.escape(plain(composer + " " + re.sub(r"<[^>]+>", "", titles[i])),
                                quote=True),
                title=titles[i])
            for i in range(len(titles)))
        blocks.append(
            '      <div class="rep-group">\n'
            '        <h2 class="rep-composer">{c}</h2>\n'
            '        <ul class="rep-works">\n{items}\n        </ul>\n'
            '      </div>'.format(c=composer, items=items))

    return (head("Repertoire &#183; CreArtBox",
                 "Every work CreArtBox has played, by composer: %d works by %d composers."
                 % (works, len(groups)),
                 SITE + "/repertoire.html")
            + """
<section style="padding:64px 0 10px">
  <div class="wrap">
    <a href="presenters.html" class="back-to-archive">&#8592; For presenters</a>

    <div class="page-folio-head" style="margin-top:22px">
      <span class="label">Repertoire</span>
      <hr class="rule" style="width:100%">
      <span class="label ital">Everything the ensemble has played</span>
    </div>
    <h1 class="sr-only">Repertoire</h1>
    <p class="lede" style="margin-top:34px;max-width:58ch">
      {works} works by {composers} composers, from the first season to this one. A programme
      can be built from any of it: write to <a href="mailto:{contact}">{contact}</a>.
    </p>

    <div class="rep-search">
      <label for="rep-q" class="label">Find a composer or a work</label>
      <input id="rep-q" type="search" placeholder="Brahms, quintet, flute..." autocomplete="off" data-rep-search>
      <span class="rep-count" data-rep-count aria-live="polite">{works} works</span>
    </div>
  </div>
</section>

<section class="section" style="padding-top:10px">
  <div class="wrap">
    <div class="rep-list" data-rep-list>
{blocks}
    </div>
    <p class="rep-empty" data-rep-empty hidden>Nothing here by that name. Write to
      <a href="mailto:{contact}">{contact}</a> and ask: the list is what has been played,
      not what can be.</p>
  </div>
</section>
""".format(blocks="\n".join(blocks), works=works, composers=len(groups), contact=CONTACT)
            + foot())


# -------------------------------------------------------------------- main

def write(path, wanted, check, stale):
    current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    if current == wanted:
        return
    stale.append(path)
    if not check:
        open(path, "w", encoding="utf-8").write(wanted)


def main():
    check = "--check" in sys.argv
    stale = []
    write("presenters.html", booking_page(), check, stale)
    write("repertoire.html", repertoire_page(), check, stale)

    if check:
        if stale:
            print("the presenters pages are out of date:")
            for p in stale:
                print("  -", p)
            print("\nRun: python3 tools/build_presenters.py")
            return 1
        groups = repertoire()
        print("presenters up to date: %d programme(s), %d works by %d composers"
              % (len(PROGRAMS), sum(len(w) for _, w in groups), len(groups)))
    else:
        print("wrote %d file(s)" % len(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
