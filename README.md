# CreArtBox · website

The CreArtBox website, migrated from Shopify to a static site hosted on
GitHub Pages. Eventbrite handles ticketing; the donate form posts to a
configurable payment URL (Stripe Payment Link, Donorbox, Givebutter, etc).

The design is the "Program" aesthetic from the Claude design handoff:
cream paper, navy ink, yellow stamp; sticky masthead with newspaper-style
nav strip; EB Garamond throughout; framed plates with figure captions;
program tables, drop caps, multi-column body, dark "ink" footer.

## File layout

```
.
├── index.html         Home (cover, mission, next concert, calls, donate strip)
├── about.html         About - bio, ensemble, board & staff, history, supporters
├── concerts.html      Season 26/27, featured concert, calendar, touring
├── projects.html      Productions catalogue (Two Roads, AWAVE, Visuality,
│                       Noctum, London the Show, Cre.Art Project), ADAMR, streaming
├── opportunities.html Open calls (Composer-in-Residence, Scores, Visual
│                       Artists), FAQ, internships, volunteering
├── media.html         Videos, audio (Bandcamp), photographs, CreArt Magazine,
│                       live podcast, streaming
├── news.html          Latest news, press releases, press quotes, newsletter
├── support.html       Donate (live calculator), mail/wire/DAF, supporters
├── classical-concerts-nyc.html
│                      Coming to a concert: the hall, getting there,
│                       start and running times, prices, FAQ
├── composer-opportunities.html
│                      Alias, canonical to opportunities.html
├── sitemap.xml        Written by tools/build_seo.py
├── robots.txt         Written by tools/build_seo.py
├── docs/              Working notes, not part of the site
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

## Calendar programmes (single source of truth)

The programme shown for each row of `concerts.html` is **generated** from
that concert's own page, so the index and the concert page can never
disagree. After editing any programme, run:

```bash
python3 tools/sync_calendar_programs.py          # rewrite the index
python3 tools/sync_calendar_programs.py --check  # fail if out of sync
```

Edit programmes only on the concert page (`concerts/*.html`, inside
`<section class="event-program">`), never in `concerts.html`.

Rows whose concert page has no structured programme - a residency, or a
date not yet programmed - keep a hand-written line and are marked
`data-program-manual` in `concerts.html`; the script leaves those alone.

Where a programme, venue or on-sale date is not known, leave it out.
The site states facts and stays silent otherwise: no "to be announced",
no "TBA", no "coming soon".

## The home page's "next event"

Also generated, from the **first row** of `concerts.html` and that
concert's own page - title, series, hero image, opening paragraph and
sidebar facts:

```bash
python3 tools/sync_next_event.py          # rewrite the block
python3 tools/sync_next_event.py --check  # fail if out of date
```

It lives between `<!-- NEXT EVENT ... -->` markers in `index.html`; do
not edit inside them. To change what the home page says, edit the
concert page and run the script.

Calendar rows are in date order, so this stays honest only if the
calendar does: **move a concert to the archive once it has happened**
and the next one is promoted automatically. The block advertised
Festival ADAR 2026 for a month after the festival ended because it was
maintained by hand.

## The brand page

`brand.html` is the public identity page: the marks, the palette with
real contrast figures, the type and layout rules, and every file as a
download. Two blocks in it are generated, along with the zip:

```bash
python3 tools/build_brand_page.py          # rewrite the blocks + zip
python3 tools/build_brand_page.py --check  # fail if out of date
```

- the palette is read from the **brand block in `assets/styles.css`**, so
  the hexes and the contrast ratios on the page are the ones that ship;
- the download grid is read from **the files in `brand/`**, with their
  real dimensions, aspect, colours and weight;
- `downloads/creartbox-brand-assets.zip` is rebuilt from the same files
  (with fixed timestamps, so `--check` is stable).

Drop a new SVG into `brand/` and run the script: it appears on the page,
on the correct light or dark card, and goes into the zip. The prose
between the markers is hand-written and left alone.

## Concert posters

One A3 poster per New York Series production - the ensemble's own new
programmes, the same set the calendar marks:

```bash
python3 tools/build_posters.py          # write posters/*.html
python3 tools/build_posters.py --check  # fail if out of date
node tools/render_posters.js            # then PDF + PNG at 150dpi
```

Title, date, time, venue, programme and players are read from the
concert page, so a poster cannot advertise a programme the site no
longer lists. Edit the concert page and run both steps again.

The foot carries the NYC Cultural Affairs and NYSCA logos with the
credit line the archive pages use. Both logos are white artwork, which
is why they sit straight on the black ground.

The renderer waits on `document.fonts.ready` and reports if Literata
failed to load, since a poster caught in the fallback face looks fine
until it reaches a printer.

## The CreArtBox biography

The same text sits on `about.html`, on `presenters.html`, in the press
downloads and in the dossier, so it is written once, in `BIOS` in the
script, and pushed to all of them:

```bash
python3 tools/build_org_bio.py            # the page and the .txt files
node tools/render_press_bios.js           # then the four PDFs
python3 tools/build_presenters.py         # the presenters page follows
python3 tools/build_org_bio.py --check    # fail if out of date
```

Four lengths: short at most 500 characters, medium at most 1500, web at
most 2000, long unbounded. `ORDER` lists them longest first, as the tabs
read. The web version is what both pages show; the long one is for a
press desk or a dossier that asks for everything, and is a download.
`tools/build_presenters.py` imports `BIOS["web"]` rather than keeping a
second copy, so the two pages cannot drift apart.

These are separate texts rather than cuts of one, because a press desk
picks between them; the script refuses to write a version that is over
its limit rather than trimming one behind your back. The tab on the page
counts the text it is describing, so the figure cannot drift.

Adding a fifth length means an entry in `BIOS` and `LIMITS`, a place in
`ORDER`, and three pieces of markup on `about.html`: the tab button, the
`bio-version` block with its copy button, and the download link.

## Artist pages

One page per member of the ensemble under `artists/`, each with the short
biography and the full one:

```bash
python3 tools/build_artist_pages.py          # write artists/*.html
python3 tools/build_artist_pages.py --check  # fail if out of date
```

The biographies live in `ARTISTS` in the script, and every word in them is
the artist's own. The long one is reproduced exactly as it stands on their
website or in the press document they supplied; the short one is theirs
too, trimmed rather than rewritten. **Nothing may be added.** If a fact is
not in the source it does not go on the page - ask the artist.

Each page offers the biography at three lengths, chosen by the switch in
the sidebar: **full**, **medium** (`MEDIUM_CHARS`, 1500) and **short**
(`SHORT_CHARS`, 500). An artist who supplies their own three gets those
verbatim, under `versions`; for everyone else the shorter two are the
opening of the full one, cut at a sentence break and never mid-word. Either
way a press desk can take any of them and quote it as the artist wrote it.
Change either constant and re-run to move the boundaries. All three are
in the page, so the switch never waits on the network, and each button
says how long its own version is.

Under every version, whatever its length, the page says the biographies
are published as the artist wrote them and are not to be altered, and
gives the artist's own address for asking for a different one.

The script also keeps the ensemble cards on `about.html` in step: one
paragraph, the player's name linking through to the page, and no list of
affiliations under it.

`tools/link_performer_bios.py` links performer names on the concert and
archive pages to these pages.

## Printed programmes

The booklet handed out at the door is also readable on the site. Drop the
PDF in `downloads/`, declare it in `PROGRAMS` in the script, and run:

```bash
pip install pymupdf                              # once
python3 tools/build_program_viewer.py            # render pages + write the page
python3 tools/build_program_viewer.py --check    # fail if out of date
```

It renders one JPEG per page at 2.5x plus a thumbnail into
`assets/programs/<slug>/`, and writes `programs/<slug>.html`. Replacing
the PDF and re-running is the whole update: the reader and the download
come from the same file, so they cannot disagree. Pages left over from a
longer previous version are deleted.

`assets/program-viewer.js` reads it as it is printed - the cover alone,
then facing pages, then whatever is left - and turns one page at a time
below 761px. Arrow keys, swipe, thumbnails, zoom and full screen are
there; nothing is parsed in the browser, so it works with the PDF
unopened.

## News

The news section is written in Markdown, one file per post, and built
into pages, an index and an RSS feed:

```bash
python3 tools/build_news.py            # write news.html, news/*.html, feed.xml
python3 tools/build_news.py --check    # fail if out of date
```

A post is `news/_posts/YYYY-MM-DD-slug.md`. It opens with a short block
of keys between `---` lines:

```
---
title: What happened
date: 2026-09-29
dek: One sentence under the headline, used on the card and in the feed.
tag: Season
image: assets/img/ensemble.jpg
alt: What the photograph shows
caption: The line printed under it.
link: Read about Currents | concerts/currents-2026.html
---
```

`link` can be repeated; each one becomes a button at the foot of the
post. The body takes paragraphs, `## ` headings, `- ` lists, `> `
quotations, `**bold**`, `*italic*`, `[links](url)`,
`![alt](path "caption")` for a photograph, and `Q: ` for an interview
question. Nothing else is needed:
the date in the filename orders the posts, the newest one leads the
index and the three newest fill the strip on the home page, between
the generated markers `<!-- NEWS ... -->`.

An interview with an artist follows one shape, so the series is
recognisable: the title is "<Number> questions for <Name>", the tag is
`Interview`, and the first paragraph says who was interviewed and why -
what we play, when, and where. That first paragraph is set as a
standfirst, above a rule. The questions themselves are lines starting
with `Q: `, and the paragraphs under each one are the answer; the page
numbers the questions itself, so they can be reordered without renumbering.

Deleting a post file deletes its page on the next run. The section is
linked from every page by:

```bash
python3 tools/sync_nav.py          # put News in the nav and the footer
python3 tools/sync_nav.py --check  # fail if a page is missing it
```

It inserts the item in front of Donate, in both shapes of navigation
strip, and in the footer under The Organization - including inside the
page templates in `tools/*.py`, so a regenerated page keeps it.

## For presenters, and the repertoire

`presenters.html` carries the programmes on offer and the About text a
presenter needs; `repertoire.html` lists every work the ensemble has
played, grouped by composer and filtered as you type. Both come from
one script:

```bash
python3 tools/build_presenters.py          # write both pages
node tools/render_dossier.js               # then the dossier PDF
python3 tools/build_presenters.py --check  # fail if out of date
```

The dossier is the presenters page printed: `@media print` decides what
it keeps (the facts, the programmes, the players, the About text and the
contact) and what it drops (the buttons, the downloads, the photographs).
Page and PDF therefore cannot say different things. The renderer needs
the brand faces; in a sandbox without a route to Google Fonts, point
`CB_FONT_CACHE` at a directory holding `fonts.css` and its woff2 files
and it serves them locally instead.

A programme is an entry in `PROGRAMS` in the script: the label, a
title, the paragraph, and the works as `(composer, work, minutes)`.
`(None, "Intermission", None)` prints the break, and the total is
added up from the durations. The About text is in `ABOUT`.

The repertoire is `data/repertoire.txt`, one work per line as
`Composer — Title` (an em dash with spaces). Composers are sorted by
surname; `SORT` in the script holds the ones the last word gets wrong
(von Weber, van Beethoven, de Falla and the rest). The search folds
accents, so "dvorak" finds Dvořák, and every term has to match.

The page is not in the navigation strip - nine items fill it - so it
sits in the footer under The Organization, and on the calendar page in
the block that was already addressed to presenters.

`PLAYERS` builds the roster (each portrait links to that player's
biography page), `PHOTOS` the downloadable photographs, and `FACTS` the
strip at the top: ensemble, formations, length, fees, base.

## The open calls

The guidelines on `calls/*.html` are written by hand. When a cycle opens
or closes, the status strip, the side cards and the buttons are edited
there and on `opportunities.html` and the home page. A composer can take
the guidelines away as a PDF:

```bash
node tools/render_calls.js      # downloads/creartbox-ca1-2026.pdf, ca2
```

As with the dossier, the PDF is the page printed: `@media print` drops
the navigation, the pills, the status strip and the buttons, puts the
side cards in a block at the top, adds a masthead with the black
wordmark, and prints the line that says where to apply, since a button
is no use on paper. Set `CB_FONT_CACHE` where Google Fonts cannot be
reached.

## The catalogue of past programmes

The presenters page leads with the two programmes on offer and then
prints every programme the ensemble has played, so a presenter can ask
for one to be revived. That catalogue is `data/programs-past.txt`:

```
Title | years | where it was played
  Composer name
  - Work | scoring | minutes
  -- I. Movement | | minutes
```

A line under a title is a composer unless it starts with `- ` (a work)
or `-- ` (a movement). **The file is hand-edited and nothing rewrites
it**: rename a programme, reorder the blocks, drop a work, and it
stays that way.

```bash
python3 tools/sync_past_programs.py          # append what the archive has and this does not
python3 tools/sync_past_programs.py --check  # list what is missing
```

The tool reads both shapes the archive keeps a programme in: the
`.pgm-list` on `archive/<slug>.html`, which has the movements, and the
older "View Program" modals in `archive.html`, which have the scoring.
Where a title is in both, the longer one wins, and a tie goes to the
page. A `.pgm-list` whose composer spans are all empty cannot be read
apart into composers, works and movements, so it is skipped and the
modal is used instead. To keep a programme out of the catalogue for
good, put `#skip ` in front of its title line; delete the block and it
comes back on the next run.

The archive marks eleven composers with a trailing asterisk and
explains it nowhere on the site. The data file keeps it; the page does
not print it.

## Search, social cards and structured data

Every indexable page carries one managed block in its head, written by
one tool and owned by nobody else:

```bash
python3 tools/build_seo.py          # rewrite the block on every page
python3 tools/build_seo.py --check  # fail if any page is stale
```

The block sits between `<!-- SEO · generated by tools/build_seo.py -->`
and `<!-- /SEO -->` and holds the canonical link, the Open Graph and
Twitter cards and a JSON-LD graph. **Run it last**, after anything else
that writes pages. The four generators that rewrite a whole page
(`build_news`, `build_presenters`, `build_artist_pages`,
`build_program_viewer`, `build_guide`) carry the existing block over
instead of wiping it, through `tools/seo_block.py`, so the order only
matters for keeping the block's contents fresh, never for losing it.

What the graph says depends on the page. Every page carries the
organization (one entity, `@id` `https://creartbox.nyc/#organization`,
with the social profiles in `sameAs`), the website, the page and its
breadcrumb. A concert page adds a `MusicEvent`: the date in the venue's
own time zone, the place, the performers, the programme as
`MusicComposition` nodes with their running times, and the ticket offer.
An archive page adds the same in the past tense, an artist page a
`Person` who is `memberOf` the ensemble, a news post a `BlogPosting`,
and any page with a `.faq` list of `<details>` a `FAQPage`.

Everything in it is read from the page itself. Two things are not, and
both live at the top of `tools/build_seo.py` where they can be checked:

- `VENUES` - street addresses, only for venues confirmed against the
  venue itself. Every other place gets its name and whatever locality
  the page states.
- `TICKETS` - prices, only as the seller showed them, with the date
  they were read in `checked`. **Re-read them before a run** if a
  listing has changed. An entry with no price still produces a valid
  offer with the link and the availability.

The same run writes `sitemap.xml` (every indexable page, `lastmod` from
git) and `robots.txt`, which names the assistant crawlers as welcome
and keeps `/newsletter/`, `/posters/` and `/docs/` out. Print-only and
mail-only pages are listed in `SKIP_DIRS`; `404.html` and the
`composer-opportunities.html` alias in `SKIP_FILES`.

Buttons that lead to a checkout carry `data-cb-track` (plus any
`data-cb-*` attributes, which travel with the event).
`initConversions()` in `site.js` hands the click to gtag, Plausible or
a dataLayer if one is ever loaded, and does nothing while none is. No
analytics script is loaded today, and a click on a ticket button is not
a sale.

## Coming to a concert

`classical-concerts-nyc.html` is the page for someone who wants to hear
the ensemble rather than read about it: the hall, the way in, the start
time, the running time, the price of a seat and eight questions with
answers.

```bash
python3 tools/build_guide.py          # write the page
python3 tools/build_guide.py --check  # fail if it is out of date
```

The season dates come from the New York Series rows of `concerts.html`,
so archiving a concert takes it off this page too. Everything else is
in the tool, next to the source it was checked against. The footer
links it under Program, through `sync_nav.py`.

## Moving a date into the archive

A concert that has happened is still on the calendar as if tickets were
coming, so once it is over it moves:

```bash
python3 tools/archive_past.py          # move everything past
python3 tools/archive_past.py --check  # fail if something is overdue
```

The dates come from the calendar rows themselves, which carry the day,
the month, the year and "to Oct 9" for a date that runs over several
days. The archive is one page: nothing writes a page of its own. For each date
that has passed the script adds an entry at the top of its year on
`archive.html` - the date, the title, what it was part of, the place, the
hero photograph from the concert page, and the programme behind a "View
Program" button - then deletes the concert page, drops the row from
`concerts.html`, and rewrites every link elsewhere that pointed at the
concert to that year in the archive, including inside `news/_posts`.

Afterwards run `sync_next_event.py`, `link_performer_bios.py` and
`build_news.py`, which the script reminds you of.

One visit, one entry: a residency and the public concert inside it are
two rows in the calendar, because tickets and dates work that way, but
in the archive they are one week. Merge them by hand after the move -
the dates of the whole visit, a line saying what the days held, the
programme of the concert behind the button - as the Kuopio entry does.

## Performer biographies

`tools/link_performer_bios.py` links every performer name in
`concerts/*.html` and `archive/*.html` to its biography on `about.html`,
and normalises the lists (role in its own column, one player per row):

```bash
python3 tools/link_performer_bios.py          # rewrite the pages
python3 tools/link_performer_bios.py --check  # fail if out of date
```

Names are linked only when the about page actually has that biography;
add the player to `MEMBERS` in the script when one is written.

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
site picks them up - no HTML changes.

To **add a new concert**, in `concerts.html`:

1. Copy one of the `<tr data-concert-series="...">` rows in the season
   table. Edit the date, title, program, venue, and `data-event` id.
2. Add the new id to the `EVENTBRITE` map in `assets/site.js`.

## Wiring the donate form

The site is static, so there is no server to open a Stripe Checkout
session. **Stripe Payment Links** are the way in: made in the dashboard,
plain URLs, and they work from a page like this one.

A Payment Link carries its own price. An amount cannot be passed in a
query string - `?amount=250` on a Stripe link does nothing - so there are
two setups, and `DONATE_LINKS` in `assets/site.js` takes either:

```js
// a) three links, "customer chooses what to pay", donor types the amount
once:    { any: "https://donate.stripe.com/..." },

// b) a link per amount as well, so Stripe charges what was picked here
monthly: { 50: "https://donate.stripe.com/...",
           100: "https://donate.stripe.com/...",
           any: "https://donate.stripe.com/..." },
```

`donateLink(freq, amount)` takes the exact amount when there is a link
for it and falls back to `any`. Until real links are pasted in, every
button opens an email carrying the amount, so nobody is turned away.

Before going live in Stripe:

- apply for the **non-profit rate** - a registered 501(c)(3) pays less
  per charge, and it is not automatic;
- make the monthly and annual links **recurring**, and leave "let
  customers adjust quantity" off;
- put the 501(c)(3) acknowledgement language in the receipt's **custom
  message**. Stripe's own receipt is a payment receipt, not the written
  acknowledgement a donor needs for a deduction.

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
   into the existing pages - the design stays the same.
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
