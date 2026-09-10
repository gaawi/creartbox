#!/usr/bin/env python3
"""Build a print poster for each New York Series concert.

One A3 portrait poster per production, written from the concert page
itself - title, date, time, venue, programme and players - so a poster
cannot advertise a programme the site no longer lists. The funder logos
sit at the foot with the credit line the archive pages already use.

    python3 tools/build_posters.py            # write posters/*.html
    python3 tools/build_posters.py --check    # fail if out of date

Rendering to PDF and PNG is a second step, because it needs a browser:

    node tools/render_posters.js

Only concerts whose series begins "New York Series" get one; those are
the ensemble's own productions, the same set the calendar marks.
"""

import glob
import os
import re
import sys

OUT = "posters"
NEW_PRODUCTION_SERIES = "New York Series"

SERIES_RE = re.compile(r'class="event-series">([^<]*)')
TITLE_RE = re.compile(r'class="event-title">([^<]*)')
WHEN_WHERE_RE = re.compile(r'class="concert-when-where">([^<]*)')
PROGRAM_RE = re.compile(r'<section class="event-program">(.*?)</section>', re.S)
ITEM_RE = re.compile(
    r'<li><span class="pgm-composer">(.*?)</span>'
    r'<span class="pgm-work">(.*?)</span></li>', re.S)
ARTIST_RE = re.compile(
    r'<li><span class="art-name">(.*?)</span>'
    r'(?:<span class="art-role">(.*?)</span>)?</li>', re.S)
MINS_RE = re.compile(r'\s*<span class="pgm-mins">.*?</span>', re.S)
TAG_RE = re.compile(r'<span class="pgm-tag">.*?</span>', re.S)
TAGS_RE = re.compile(r"<[^>]+>")


def text(fragment):
    return re.sub(r"\s+", " ", TAGS_RE.sub("", fragment)).strip()


def read(path):
    """Everything the poster needs, taken off the concert page."""
    page = open(path, encoding="utf-8").read()
    series = SERIES_RE.search(page)
    if not series or not series.group(1).strip().startswith(NEW_PRODUCTION_SERIES):
        return None

    when_where = text(WHEN_WHERE_RE.search(page).group(1))
    # "December 11, 2026 - 7:30 pm - The DiMenna Center - 450 W 37th St, ..."
    parts = [p.strip() for p in when_where.split("·")]
    date = parts[0] if parts else ""
    time = parts[1] if len(parts) > 1 and re.search(r"\d\s*(am|pm)", parts[1], re.I) else ""
    venue = " · ".join(parts[2:] if time else parts[1:])

    programme = []
    section = PROGRAM_RE.search(page)
    if section:
        for composer, work in ITEM_RE.findall(section.group(1)):
            programme.append((text(TAG_RE.sub("", composer)),
                              text(MINS_RE.sub("", work))))

    players = []
    for name, role in ARTIST_RE.findall(page):
        players.append((text(name), text(role or "")))

    return {
        "slug": os.path.splitext(os.path.basename(path))[0],
        "series": text(series.group(1)),
        "title": text(TITLE_RE.search(page).group(1)),
        "date": date, "time": time, "venue": venue,
        "programme": programme, "players": players,
    }


def render(c):
    rows = "\n".join(
        '      <li><span class="pc">{}</span><span class="pw">{}</span></li>'.format(a, b)
        for a, b in c["programme"])
    people = " &nbsp;·&nbsp; ".join(
        "{} <em>{}</em>".format(n, r) if r else n for n, r in c["players"])
    when = c["date"] + (" · " + c["time"] if c["time"] else "")

    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title} · poster</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,300..700;1,300..700&family=Literata:ital,opsz,wght@0,7..72,300..700;1,7..72,300..700&display=swap" rel="stylesheet">
<style>
  @page {{ size: A3 portrait; margin: 0; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    width: 297mm; height: 420mm; background: #070706; color: #F2EFE8;
    font-family: "Archivo", Helvetica, Arial, sans-serif;
    padding: 22mm 20mm 16mm; display: flex; flex-direction: column;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }}
  .mark img {{ height: 13mm; width: auto; display: block; }}
  .series {{
    margin-top: 20mm; font-size: 3.4mm; font-weight: 600;
    letter-spacing: 0.22em; text-transform: uppercase; color: #FFC403;
  }}
  h1 {{
    max-width: 235mm; font-family: "Literata", Georgia, serif; font-weight: 300;
    font-size: 26mm; line-height: 0.94; letter-spacing: -0.02em;
    margin: 5mm 0 0; color: #F2EFE8;
  }}
  .when {{
    /* two auto margins, here and on the foot, so the slack falls as air
       under the title and above the credits rather than mid-list */
    margin-top: auto; padding-top: 5mm; border-top: 0.4mm solid #2B2825;
    font-size: 5.4mm; font-weight: 500; font-variant-numeric: tabular-nums;
  }}
  .venue {{ margin-top: 2mm; font-size: 4.2mm; color: #C9C3B9; }}
  .pgm {{ list-style: none; padding: 0; margin: 12mm 0 0; }}
  .pgm li {{
    display: grid; grid-template-columns: 62mm 1fr; gap: 6mm;
    padding: 3.2mm 0; border-top: 0.25mm solid #2B2825; align-items: baseline;
  }}
  .pgm li:last-child {{ border-bottom: 0.25mm solid #2B2825; }}
  .pc {{ font-family: "Literata", Georgia, serif; font-size: 4.6mm; color: #F2EFE8; }}
  .pw {{ font-family: "Literata", Georgia, serif; font-style: italic;
         font-size: 4.2mm; color: #C9C3B9; line-height: 1.35; }}
  .players {{ margin-top: 8mm; font-size: 3.8mm; color: #C9C3B9; line-height: 1.7; }}
  .players em {{ font-style: normal; color: #8A847A; }}
  .foot {{ margin-top: auto; padding-top: 10mm; }}
  .site {{
    font-size: 4.4mm; font-weight: 600; letter-spacing: 0.04em; color: #FFC403;
  }}
  .fund {{
    margin-top: 7mm; padding-top: 5mm; border-top: 0.4mm solid #2B2825;
    display: flex; align-items: center; gap: 10mm;
  }}
  .fund img {{ height: 9mm; width: auto; }}
  .fund .credit {{ font-size: 2.5mm; line-height: 1.5; color: #8A847A; max-width: 105mm; }}
  .fund .lbl {{
    font-size: 2.5mm; font-weight: 600; letter-spacing: 0.2em;
    text-transform: uppercase; color: #8A847A; margin-bottom: 3mm;
  }}
</style></head>
<body>
  <div class="mark"><img src="../brand/logo-creartbox-reversed.svg" alt="CreArtBox"></div>
  <div class="series">{series}</div>
  <h1>{title}</h1>
  <div class="when">{when}</div>
  <div class="venue">{venue}</div>
  <ul class="pgm">
{rows}
  </ul>
  <div class="players">{people}</div>
  <div class="foot">
    <div class="site">creartbox.nyc</div>
    <div>
      <div class="fund">
        <div>
          <div class="lbl">Supported by</div>
          <div style="display:flex;align-items:center;gap:9mm">
            <img src="../assets/logos/nyc-cultural-affairs.png" alt="NYC Department of Cultural Affairs">
            <img src="../assets/logos/nysca.png" alt="New York State Council on the Arts">
          </div>
        </div>
        <p class="credit">This project was made possible by the New York State Council on the Arts with the support of the Office of the Governor and the New York State Legislature. CreArtBox, Inc. is a 501(c)(3) non-profit.</p>
      </div>
    </div>
  </div>
</body></html>
""".format(series=c["series"], title=c["title"], when=when,
           venue=c["venue"], rows=rows, people=people)


def main():
    check = "--check" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    wanted, stale = {}, []

    for path in sorted(glob.glob("concerts/*.html")):
        c = read(path)
        if c:
            wanted[os.path.join(OUT, c["slug"] + ".html")] = render(c)

    for path, html in wanted.items():
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if current != html:
            stale.append(path)
            if not check:
                open(path, "w", encoding="utf-8").write(html)

    # a concert that stops being a New York Series production loses its poster
    for path in glob.glob(os.path.join(OUT, "*.html")):
        if path not in wanted:
            stale.append(path + " (no longer a New York Series production)")
            if not check:
                os.remove(path)

    if check:
        if stale:
            print("posters out of date:")
            for p in stale:
                print("  -", p)
            print("\nRun: python3 tools/build_posters.py && node tools/render_posters.js")
            return 1
        print("posters up to date: {}".format(len(wanted)))
        return 0

    print("wrote {} poster(s):".format(len(wanted)))
    for p in sorted(wanted):
        print("  -", p)
    print("\nNow render them: node tools/render_posters.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
