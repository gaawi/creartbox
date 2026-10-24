# Where to list the concert and the calls

Working notes, October 2026. **Nothing here has been submitted.** No
account was created, no form was sent, no money was spent. Each entry
says what the target is, what it would take, and how far the
submission path was actually confirmed, so that whoever does it knows
what they are walking into.

Two deadlines drive the order: **Currents on 30 October 2026**, which
is days away, and the **calls for scores, closing 15 December 2026**.

Confirmation column:

- **confirmed** - the submission page was opened and it describes how
  to send a listing.
- **exists** - the site is live and clearly carries listings of this
  kind, but the submission page was not reached from here (several of
  these sites render their navigation in JavaScript and a plain fetch
  returns nothing).
- **unverified** - named from knowledge of the field, not checked.

---

## A. Currents, and the New York Series

Anything submitted this week only pays off for Currents if it is
published within days. The entries marked *for the season* are worth
doing regardless, because they will carry Winterlight in December and
the two spring dates.

| Priority | Target | Why | Confirmation |
|---|---|---|---|
| 1 | **Google Search Console** and **Bing Webmaster Tools** | Not a listing: the one thing that makes the new `sitemap.xml` useful. Verify `creartbox.nyc`, submit the sitemap, request indexing of the Currents page and the two call pages. Free, ten minutes, and it is also how you find out what people already search for. Bing matters more than its market share suggests: it feeds Copilot and, in part, ChatGPT search. | confirmed |
| 2 | **Bachtrack** (bachtrack.com) | The largest classical listings site in English, and it already carries DiMenna Center concerts, so the venue is in its database. Listings are free for presenters; it also commissions reviews. Start from bachtrack.com/contact. | exists |
| 3 | **City Guide New York** (cityguideny.com) | Runs a classical and opera calendar for the city and takes submissions through a form at `/addcalendar.cfm`. Free. | confirmed |
| 4 | **NYC-ARTS** (nyc-arts.org) | The WNET/Thirteen cultural calendar for the metro area, and the most "institutional" of the free listings. Non-profit arts organizations are its subject. | exists |
| 5 | **NYC Tourism + Conventions** (nycgo.com) | The official city visitor calendar. Reaches people deciding what to do in New York that week rather than people looking for chamber music. | exists |
| 6 | **Time Out New York** | High traffic, editorially selected rather than open. Better treated as a press pitch for a season or a production than as a listing. | unverified |
| 7 | **WQXR / New Sounds** (wqxr.org) | New York's classical station. Their listings and on-air mentions are editorial; the open call for scores and the new work in the programmes are the angle, not the date. | unverified |
| 8 | **The Violin Channel, I Care If You Listen, Classical Post** | Trade press for the new-music audience specifically. Again a pitch, not a form. *Pressure and Release* in April, a whole evening from an open call, is a better story than a single concert. | unverified |
| 9 | **Live Music Project**, **ClubFreeTime** | Aggregators that skew to free concerts. Low effort, low return unless a date is free. | exists |

Two things that are not listings but do the same work:

- **Eventbrite's own discovery**. The listing already exists and is the
  canonical source the site's structured data points at. Check that
  its category, tags and "online/in person" fields are filled in: that
  is what Eventbrite's internal search ranks on, and it costs nothing.
- **The venue.** The DiMenna Center publishes a performance calendar.
  Ask whether the New York Series dates are on it.

---

## B. The calls for scores, CA1/2026 and CA2/2026

The audience here is composers, and they look in a small number of
well-known places. Deadline 15 December 2026, so there is time to do
this properly.

| Priority | Target | Why | Confirmation |
|---|---|---|---|
| 1 | **Scorefolio** (scorefol.io/opportunities) | A composer-facing opportunities board that explicitly accepts listings for calls run elsewhere. Check its terms for whether listing is free. | confirmed |
| 2 | **American Composers Forum** (composersforum.org) | Membership organization with an opportunities feed; its audience is exactly CA2/2026's. | exists |
| 3 | **New Music USA** (newmusicusa.org) | The field's central hub in the United States. Its opportunities listing has moved under `/get-funding/`; confirm whether third-party calls are still accepted. | exists |
| 4 | **NYFA Opportunities** (nyfa.org/opportunities) | The New York Foundation for the Arts classifieds, widely read by artists in the state. It blocks automated fetches, so open it in a browser. | exists |
| 5 | **Chamber Music America** | Classifieds for the chamber music field specifically, which is narrower and better targeted than a general composer board. Members only, possibly. | unverified |
| 6 | **Society of Composers, Inc. (SCI)** and **ISCM** sections | Academic and international reach; good for CA1/2026. | unverified |
| 7 | **Composition:Today**, **The Composer's Site**, call-for-scores aggregator newsletters | Long-running European-leaning boards. Cheap to submit, moderate return. | unverified |
| 8 | **University composition departments** | A short email to the heads of composition at a dozen programmes reaches more serious applicants than most boards, and costs nothing. The eleven composers already chosen through the call are the credential to lead with. | n/a |

A note on the fee. Several boards flag calls that charge an entry fee,
and some composers filter them out. $20 with waivers is at the low end,
and the listings that let you add a line should say what the fee pays
for, the same way the call pages do.

---

## C. The entity itself

These are slower and they are what makes an assistant answer "who are
CreArtBox" correctly, rather than from a press release it found once.

| Target | Why |
|---|---|
| **Wikidata** | A Wikidata item for CreArtBox, Inc. - founded 2013, New York, chamber ensemble, founders, official website - is the single highest-leverage entry in this document for AI answers. It is free, it takes an hour, and it is the backbone most knowledge panels and assistants resolve names against. The site's JSON-LD already declares the same facts, which is what a Wikidata item needs to be corroborated by. |
| **MusicBrainz** | The equivalent for recordings and performers. Useful if the Bandcamp and Spotify catalogue grows. |
| **Google Business Profile** | Only if the Queens address is a place people may visit. For an ensemble that performs at someone else's venue, this is usually not worth the verification. |
| **Spotify for Artists** | Separate from all of this, the Spotify tile on `media.html` points at an artist URL that does not resolve. Whoever controls the Spotify catalogue should supply the real one. |

---

## What not to do

- Do not pay for directory links or "SEO packages". Paid links are
  what Google's link spam policy is about, and they put a clean site
  at risk for nothing.
- Do not submit the same text to twenty boards. Two or three good
  listings with real copy beat twenty thin ones, and the thin ones are
  what gets a site filtered.
- Do not treat a click on a ticket button as a sale. The site can now
  count the clicks; only Eventbrite knows the sales.
