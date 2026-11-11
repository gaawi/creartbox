#!/usr/bin/env python3
"""Lay out the ticket-lottery graphics, one HTML file per format.

    python3 tools/build_lottery_art.py          # write promo/*.html
    node tools/render_lottery_art.js            # render them to JPEG

Four formats, the same four the concert artwork already uses: a square
for a feed, a portrait, a story and a landscape for a link card. They
share one photograph family, one typeface pair and one signal colour, so
the set reads as one campaign rather than four pictures.

The brand is the site&#x27;s own: Literata for display, Archivo for
everything else, #FFC403 on #070706, which is what assets/styles.css
calls --senal on --sala. Nothing here invents a colour.

The photographs are from Currents, on 30 October, and are served from
the archive CDN rather than copied into the repository. The HTML lives
in promo/, which is kept out of the sitemap and out of robots.txt the
same way posters/ is: it is a layout file for a renderer, not a page.
"""

import html
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "promo"
CDN = ("https://creartbox-archive.b-cdn.net/archive-creartbox/"
       "2026-10-30-currents-photos/web")

# Everything the graphics say. Each line is on the site and was checked
# there: the date and time and hall on the concert page, the deadline and
# the address on lottery.html.
LINE_TOP = "CreArtBox &#183; New York Series"
BIG_1 = "Ten pairs of tickets,"
BIG_2 = "free."
CONCERT = "Winterlight &#183; Stravinsky&#x27;s Petroushka"
HOW_1 = "Email info@creartbox.nyc"
HOW_2 = "Subject: WINTERLIGHT LOTTERY"
HOW_3 = "Tell us why you would like to come"
DEADLINE = "Entries close December 3"
FOOT = "December 11, 2026 &#183; 7:30 PM &#183; The DiMenna Center, New York"

# (slug, width, height, photograph, how the photograph is framed, scale)
# The wide scene for the wide formats, the warmer close one wherever
# the crop is tight: 4:5 and 9:16 cut a landscape photograph down to
# a slice, and a slice of a hall seen from the back is a brown wall.
FORMATS = [
    ("square",    1080, 1080, "_DSC0656.jpg", "50% 42%", 1.00),
    ("portrait",  1080, 1350, "_DSC0670.jpg", "52% 45%", 1.02),
    ("story",     1080, 1920, "_DSC0670.jpg", "47% 52%", 1.08),
    ("landscape", 1200,  628, "_DSC0656.jpg", "50% 46%", 0.82),
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{slug}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,300..700;1,300..700&family=Literata:ital,opsz,wght@0,7..72,300..700;1,7..72,300..700&display=swap" rel="stylesheet">
<style>
  :root {{
    --sala:   #070706;
    --senal:  #FFC403;
    --papel:  #F2EFE8;
    --papel-medio: #C9C3B9;
    --display: "Literata", Georgia, serif;
    --texto:   "Archivo", Helvetica, Arial, sans-serif;
    --k: {scale};
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: {w}px; height: {h}px; background: var(--sala); }}
  body {{
    position: relative;
    overflow: hidden;
    font-family: var(--texto);
    color: var(--papel);
    -webkit-font-smoothing: antialiased;
  }}

  .shot {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: {focus};
    filter: saturate(1.22) contrast(1.06) brightness(1.06);
  }}
  /* Dark at the top and bottom so the type has somewhere to sit, and the
     middle left alone so the hall is still a photograph. */
  .veil {{
    position: absolute;
    inset: 0;
    background:
      linear-gradient(to bottom,
        rgba(7,7,6,.90) 0%, rgba(7,7,6,.62) 26%, rgba(7,7,6,.10) 46%,
        rgba(7,7,6,.30) 60%, rgba(7,7,6,.90) 80%, rgba(7,7,6,.98) 100%);
  }}
  /* The warm half of winter light. Soft-light keeps the wood wooden
     instead of washing an orange film over the photograph. */
  .warm {{
    position: absolute;
    inset: 0;
    mix-blend-mode: soft-light;
    background:
      radial-gradient(90% 55% at 50% 52%, rgba(255,176,40,.85), transparent 70%),
      linear-gradient(to bottom, rgba(255,140,20,.30), transparent 55%);
  }}
  .glow {{
    position: absolute;
    left: -10%; right: -10%;
    top: calc(14% - 2px); height: 34%;
    background: radial-gradient(60% 100% at 30% 50%, rgba(255,196,3,.16), transparent 70%);
  }}
  /* Winter light: a few specks of the signal colour, the way the hall
     photograph already scatters it. */
  .flecks {{
    position: absolute;
    inset: 0;
    background-image:
      radial-gradient(2px 2px at 14% 23%, rgba(255,196,3,.55), transparent 60%),
      radial-gradient(1.5px 1.5px at 78% 17%, rgba(255,196,3,.40), transparent 60%),
      radial-gradient(2px 2px at 62% 31%, rgba(242,239,232,.30), transparent 60%),
      radial-gradient(1.5px 1.5px at 31% 12%, rgba(242,239,232,.26), transparent 60%),
      radial-gradient(2.5px 2.5px at 88% 38%, rgba(255,196,3,.30), transparent 60%),
      radial-gradient(1.5px 1.5px at 8% 44%, rgba(242,239,232,.20), transparent 60%);
  }}

  .frame {{
    position: absolute;
    inset: calc(26px * var(--k));
    border: 1px solid rgba(255,196,3,.42);
    pointer-events: none;
  }}

  .stack {{
    position: absolute;
    inset: calc(58px * var(--k));
    display: grid;
    grid-template-rows: auto 1fr auto;
  }}
  .bottom {{ align-self: end; }}

  .kicker {{
    font-size: calc(21px * var(--k));
    font-weight: 600;
    letter-spacing: .20em;
    text-transform: uppercase;
    color: var(--senal);
  }}

  .big {{
    margin-top: calc(26px * var(--k));
    font-family: var(--display);
    font-weight: 500;
    font-size: calc({big}px * var(--k));
    line-height: 1.02;
    letter-spacing: -.015em;
  }}
  .big em {{ font-style: italic; color: var(--senal); }}

  .concert {{
    margin-top: calc(18px * var(--k));
    font-family: var(--display);
    font-style: italic;
    font-size: calc(30px * var(--k));
    color: var(--papel-medio);
  }}

  .rule {{
    width: calc(96px * var(--k));
    height: 2px;
    background: var(--senal);
    margin: calc(26px * var(--k)) 0 calc(22px * var(--k));
  }}

  .how {{ font-size: calc(26px * var(--k)); line-height: 1.58; color: var(--papel); }}
  .how strong {{ font-weight: 600; color: var(--senal); letter-spacing: .02em; }}
  .how span {{ color: var(--papel-medio); }}

  .deadline {{
    margin-top: calc(16px * var(--k));
    display: inline-block;
    padding: calc(9px * var(--k)) calc(16px * var(--k));
    border: 1px solid var(--senal);
    font-size: calc(20px * var(--k));
    font-weight: 600;
    letter-spacing: .13em;
    text-transform: uppercase;
    color: var(--senal);
  }}

  .foot {{
    font-size: calc(19px * var(--k));
    letter-spacing: .09em;
    text-transform: uppercase;
    color: var(--papel-medio);
  }}
</style>
</head>
<body>
  <img class="shot" src="{cdn}/{photo}" alt="">
  <div class="veil"></div>
  <div class="warm"></div>
  <div class="glow"></div>
  <div class="flecks"></div>
  <div class="frame"></div>
  <div class="stack">
    <div>
      <div class="kicker">{top}</div>
      <div class="big">{big1}<br><em>{big2}</em></div>
      <div class="concert">{concert}</div>
    </div>
    <div></div>
    <div class="bottom">
      <div class="rule"></div>
      <div class="how">
        {how1}<br>
        Subject: <strong>WINTERLIGHT LOTTERY</strong><br>
        <span>{how3}</span>
      </div>
      <div class="deadline">{deadline}</div>
      <div class="foot" style="margin-top:calc(26px * var(--k))">{foot}</div>
    </div>
  </div>
</body>
</html>
"""

# The headline size per format, before the scale factor
BIG_PX = {"square": 76, "portrait": 76, "story": 80, "landscape": 68}


def main():
    os.chdir(ROOT)
    os.makedirs(OUT, exist_ok=True)
    for slug, w, h, photo, focus, scale in FORMATS:
        page = PAGE.format(
            slug=slug, w=w, h=h, scale=scale, focus=focus,
            cdn=CDN, photo=photo, big=BIG_PX[slug],
            top=LINE_TOP, big1=BIG_1, big2=BIG_2, concert=CONCERT,
            how1=HOW_1, how3=HOW_3, deadline=DEADLINE, foot=FOOT)
        path = os.path.join(OUT, "lottery-%s.html" % slug)
        open(path, "w", encoding="utf-8").write(page)
        print("wrote %-30s %dx%d" % (path, w, h))
    print("\nNow: node tools/render_lottery_art.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
