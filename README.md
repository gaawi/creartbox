# CreArtBox · website

The CreArtBox website, migrated from Shopify to a static site hosted on
GitHub Pages. Eventbrite handles ticketing; the donate form posts to a
configurable payment URL (Stripe Payment Link, Donorbox, Givebutter, etc).

The design is the "Programme" aesthetic from the Claude design handoff:
cream paper, navy ink, yellow stamp; sticky masthead with newspaper-style
nav strip; EB Garamond throughout; framed plates with figure captions;
programme tables, drop caps, multi-column body, dark "ink" footer.

## File layout

```
.
├── index.html         Home (cover, mission, next concert, calls, donate strip)
├── about.html         About — bio, ensemble, board & staff, history, supporters
├── concerts.html      Season 26/27, featured concert, calendar, touring
├── projects.html      Productions catalogue (Two Roads, AWAVE, Visuality,
│                       Noctum, London the Show, Cre.Art Project), ADAMR, streaming
├── opportunities.html Open calls (Composer-in-Residence, Scores, Visual
│                       Artists), FAQ, internships, volunteering
├── media.html         Videos, audio (Bandcamp), photographs, CreArt Magazine,
│                       live podcast, streaming
├── news.html          Latest news, press releases, press quotes, newsletter
├── support.html       Donate (live calculator), mail/wire/DAF, supporters
├── 404.html
├── assets/
│   ├── styles.css     The complete design system (one file)
│   └── site.js        Theme toggle, mobile menu, Eventbrite wiring, donate
│                       calculator, classifieds expand, concert filter tabs
├── reference/         Frozen Shopify content for reference only
└── README.md
```

No build step. Open `index.html` in a browser and it works.

## Sitemap (matches the agreed structure)

```
Home   About   Concerts   Projects   Opportunities   Media   News   Support
```

Subsections inside pages (anchor links from the footer and from the index):

- `about.html#ensemble`, `#board`, `#history`, `#supporters`
- `projects.html#adamr`, `#streaming`
- `media.html#magazine`, `#podcast`

## Local preview

```sh
# Any static server. Examples:
python3 -m http.server 8000
# then open http://localhost:8000

# or
npx serve .
```

## Deploy to GitHub Pages

```sh
git push origin main
```

Then in the repository on GitHub: **Settings → Pages → Source: Deploy
from a branch → Branch: `main` / root**. The site goes live at
`https://<owner>.github.io/<repo>/` within a minute or two.

For the production custom domain `creartbox.nyc`:

1. In the repo, add a `CNAME` file containing `creartbox.nyc`.
2. At the DNS registrar, add the four GitHub Pages A records pointing
   `creartbox.nyc` to GitHub, plus a `CNAME` record `www →
   <owner>.github.io`.
3. In **Settings → Pages**, confirm the custom domain and tick "Enforce
   HTTPS" once the certificate provisions.

## Wiring tickets to Eventbrite

All "Get tickets" buttons carry a `data-event="..."` attribute. The
mapping from event id → Eventbrite URL lives in one place:

`assets/site.js`, near the top:

```js
const EVENTBRITE = {
  "threshold-2026-06-06":   "https://www.eventbrite.com/e/...",
  "tworoads-2026-09-18":    "https://www.eventbrite.com/e/...",
  "afterlight-2026-10-04":  "https://www.eventbrite.com/e/...",
  "noctum-2026-11-14":      "https://www.eventbrite.com/e/...",
  "winter-2026-12-11":      "https://www.eventbrite.com/e/...",
  "awave-2027-02-06":       "https://www.eventbrite.com/e/...",
  "season-subscription":    "https://www.eventbrite.com/o/creartbox",
};
```

Set the real Eventbrite URLs there and every ticket button across the
site picks them up — no HTML changes.

To **add a new concert**, in `concerts.html`:

1. Copy one of the `<tr data-concert-series="...">` rows in the season
   table. Edit the date, title, programme, venue, and `data-event` id.
2. Add the new id to the `EVENTBRITE` map in `assets/site.js`.

## Wiring the donate form

All donate buttons carry `data-donate`. The destination URL lives at the
top of `assets/site.js`:

```js
const DONATE_URL = "https://buy.stripe.com/your_payment_link";
```

The donate page form (`support.html`) appends `?amount=...&frequency=...`
so a Stripe Payment Link can pre-fill the amount via Stripe's URL
parameters, or you can wire it to **Donorbox**, **Givebutter**, or any
other processor by changing only this one constant.

Until that URL is set the buttons fall back to
`mailto:info@creartbox.nyc?subject=Donation`.

## Images

All image slots are currently rendered as cross-hatch placeholders with
a caption. Replace each one by swapping its `<div class="imedia
placeholder">…</div>` for:

```html
<div class="imedia duotone">
  <img src="assets/img/your-photo.jpg" alt="Description">
</div>
```

Add the file under `assets/img/`. Keep the `duotone` class if you want
the print-style sepia/grayscale treatment; remove it for full colour.

## Adding Supabase later

We did not need a database for v1, but if/when content grows beyond
hand-editing, a Supabase-backed flow drops in cleanly:

1. Create tables `events`, `news`, `opportunities`, `supporters`.
2. Add a small build step (a Node script or a GitHub Action) that
   reads from Supabase at build time and writes the HTML fragments
   into the existing pages — the design stays the same.
3. Alternatively, fetch on the client at runtime: include
   `@supabase/supabase-js` from a CDN in `assets/site.js` and replace
   the static `<tbody>` of the concerts table with rows rendered from
   the events table.

The design system is built around the data; the data swap is
non-structural.

## Design tokens (CSS variables)

All colours and key sizes are CSS variables at the top of
`assets/styles.css`:

```
--paper       #f4ecda      cream paper
--ink         #1b3447      navy ink
--ink-2       #2f4b60      secondary ink
--ink-soft    #5d7384      muted ink
--yellow      #fbda41      stamp yellow
--red         #8a2a1f      stamp red
--serif       EB Garamond  the only typeface
--maxw        1320px       page container
--gutter      clamp(20px, 4vw, 56px)
```

Dark "night" mode is provided by `:root[data-theme="dark"]` and toggled
by the `☾` button in the masthead.

## Reference

`reference/` contains a frozen copy of selected Shopify Liquid templates
(about, donate, board, press, artists) for content cross-checking. They
are not used by the site and can be deleted once content has been
verified.
