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
# The stage with the Petroushka backdrop, cropped clean out of the
# concert artwork. It is the brightest thing the ensemble has: blue,
# red and gold, a lit stage and a full house, which is what a holiday
# giveaway should look like. A dark hall is beautiful and reads as a
# requiem.
SHOT = "../assets/img/promo/winterlight-stage.jpg"

# Everything the graphics say. Each line is on the site and was checked
# there: the date and time and hall on the concert page, the deadline and
# the address on lottery.html.
STICKERS = ["Holiday giveaway", "Ten pairs of tickets"]
STICKER_GOLD = "Enter by Dec 3"
KICKER = "CreArtBox"
BIG = "Our holiday gift:<br>free tickets to<br><em>Winterlight</em>"
SUB = "Friday, December 11 &#183; The DiMenna Center"
HOW_1 = "Write to <b>info@creartbox.nyc</b>"
HOW_2 = "Subject: <b>WINTERLIGHT LOTTERY</b>"
HOW_3 = "One sentence on why you would like to come"
FOOT = "creartbox.nyc"

# (slug, width, height, photograph, how the photograph is framed, scale)
# The wide scene for the wide formats, the warmer close one wherever
# the crop is tight: 4:5 and 9:16 cut a landscape photograph down to
# a slice, and a slice of a hall seen from the back is a brown wall.
FORMATS = [
    ("square",    1080, 1080, "50% 50%", 1.00),
    ("portrait",  1080, 1350, "50% 50%", 1.02),
    ("story",     1080, 1920, "50% 50%", 1.06),
    ("landscape", 1200,  628, "50% 48%", 0.80),
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
  }}
  /* The photograph is already lit and already coloured. All it needs is
     somewhere dark for the words to sit, top and bottom. */
  .veil {{
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom,
      rgba(7,7,6,.88) 0%, rgba(7,7,6,.40) 20%, rgba(7,7,6,0) 38%,
      rgba(7,7,6,0) 52%, rgba(7,7,6,.72) 76%, rgba(7,7,6,.97) 100%);
  }}

  .stack {{
    position: absolute;
    inset: calc(54px * var(--k));
    display: grid;
    grid-template-rows: auto 1fr auto;
  }}

  /* Stickers: a label slapped on, which is what a giveaway looks like
     and what a programme note never does. */
  .stickers {{ display: flex; flex-direction: column; align-items: flex-start;
               gap: calc(9px * var(--k)); }}
  .sticker, .sticker-gold {{
    display: inline-block;
    padding: calc(9px * var(--k)) calc(15px * var(--k));
    font-size: calc(21px * var(--k));
    font-weight: 700;
    letter-spacing: .13em;
    text-transform: uppercase;
    background: var(--papel);
    color: var(--sala);
    box-shadow: 0 calc(3px * var(--k)) calc(16px * var(--k)) rgba(0,0,0,.45);
  }}
  .sticker:nth-child(1) {{ transform: rotate(-1.8deg); }}
  .sticker:nth-child(2) {{ transform: rotate(1.2deg); }}
  .sticker-gold {{ background: var(--senal); transform: rotate(-1.1deg); }}

  .bottom {{ align-self: end; }}
  .kicker {{
    font-size: calc(18px * var(--k));
    font-weight: 600;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--senal);
  }}
  .kicker::after {{
    content: "";
    display: block;
    width: calc(54px * var(--k));
    height: 2px;
    background: var(--senal);
    margin-top: calc(9px * var(--k));
  }}
  .big {{
    margin-top: calc(16px * var(--k));
    font-family: var(--display);
    font-weight: 500;
    font-size: calc({big}px * var(--k));
    line-height: 1.06;
    letter-spacing: -.015em;
    text-shadow: 0 calc(2px * var(--k)) calc(22px * var(--k)) rgba(7,7,6,.75);
  }}
  .big em {{ font-style: italic; color: var(--senal); }}
  .sub {{
    margin-top: calc(14px * var(--k));
    font-family: var(--display);
    font-style: italic;
    font-size: calc(26px * var(--k));
    color: var(--papel-medio);
  }}
  .how {{
    margin-top: calc(20px * var(--k));
    font-size: calc(23px * var(--k));
    line-height: 1.55;
    color: var(--papel-medio);
  }}
  .how b {{ color: var(--papel); font-weight: 600; }}
  .foot {{
    margin-top: calc(22px * var(--k));
    font-size: calc(18px * var(--k));
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--senal);
  }}
</style>
</head>
<body>
  <img class="shot" src="{shot}" alt="">
  <div class="veil"></div>
  <div class="stack">
    <div class="stickers">
      {stickers}
      <span class="sticker-gold">{gold}</span>
    </div>
    <div></div>
    <div class="bottom">
      <div class="kicker">{kicker}</div>
      <div class="big">{bigtext}</div>
      <div class="sub">{sub}</div>
      <div class="how">{how1}<br>{how2}<br>{how3}</div>
      <div class="foot">{foot}</div>
    </div>
  </div>
</body>
</html>
"""

# The headline size per format, before the scale factor
BIG_PX = {"square": 62, "portrait": 62, "story": 66, "landscape": 54}


def main():
    os.chdir(ROOT)
    os.makedirs(OUT, exist_ok=True)
    for slug, w, h, focus, scale in FORMATS:
        stickers = "".join(
            '<span class="sticker">{}</span>'.format(t) for t in STICKERS)
        page = PAGE.format(
            slug=slug, w=w, h=h, scale=scale, focus=focus,
            shot=SHOT, big=BIG_PX[slug], stickers=stickers,
            gold=STICKER_GOLD, kicker=KICKER, bigtext=BIG, sub=SUB,
            how1=HOW_1, how2=HOW_2, how3=HOW_3, foot=FOOT)
        path = os.path.join(OUT, "lottery-%s.html" % slug)
        open(path, "w", encoding="utf-8").write(page)
        print("wrote %-30s %dx%d" % (path, w, h))
    print("\nNow: node tools/render_lottery_art.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
