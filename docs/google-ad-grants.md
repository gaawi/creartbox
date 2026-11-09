# The $10,000 Google Ad Grant: how to set it up

Working notes, October 2026.

**What I cannot do:** log into your Google Ads account. The grant is
tied to your Google for Nonprofits account, it needs your credentials,
and it spends real ad inventory. Every step below is one you take.

**What I did do:** build the whole account as import files, with every
headline and description checked against Google's character limits, and
every claim checked against the site. `docs/ads/` holds the import files
for Google Ads Editor, and `docs/ads/build_ads.py` is what wrote them,
so the copy can be edited in one place and rewritten with one command.

```bash
python3 docs/ads/build_ads.py
```

**If someone else is doing the work in the account**, hand them
`docs/ads/BRIEF-google-ads-agent.md` instead of this file. It is the
same account, written as operating instructions: the verified fact
sheet that bounds what the ads may claim, the settings the CSVs cannot
carry, the negative keyword lists, and which of Google's thresholds I
could quote from Google and which I could not.

---

## 1. The one thing that blocks everything else

**Ad Grants requires working conversion tracking and at least one
conversion recorded per month.** No tracking, no grant. The site
currently loads no analytics at all, so this is step one and it is your
decision, not mine.

The wiring is already there. Ticket and apply buttons carry
`data-cb-track`, and `initConversions()` in `assets/site.js` already
hands every click to `gtag`, Plausible or a `dataLayer`. Adding Google
Analytics 4 means adding the tag and nothing else:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

Send me the measurement ID and I will put it on all 141 pages through
`tools/build_seo.py`, so it cannot drift.

Then, in GA4, mark these as key events and import them into Google Ads
as conversions:

| Event | Fires when | Counts as |
|---|---|---|
| `tickets` | someone clicks a ticket button | outbound click to Eventbrite |
| `apply` | someone clicks Apply on a call | outbound click to Tally |
| `calendar` | someone opens the calendar from the guide | a soft conversion |

**Be honest with yourself about what these are.** They count people
leaving for the checkout, not people who paid. Eventbrite and Tally
hold the real numbers, and the two should be compared each month, never
confused. Google only needs a conversion signal; you need the truth.

---

## 2. The rules that shape the account

Rechecked on 9 November 2026 against Google's own help pages. The
Policy Compliance Guide itself still will not load from here, so two
things below are still **unverified** and are marked as such;
`docs/ads/BRIEF-google-ads-agent.md` separates the quoted from the
unverified line by line, and is the version to work from.

- **5% click-through rate, account-wide, every month.** Two months
  below it and the account is deactivated. This is the rule that kills
  grant accounts, and it is why the structure below is narrow: phrase
  and exact match only, no broad match, and a brand campaign whose
  click-through rate props up the account average. A new account is not
  reviewed against it "until 90 days old", which is the window to find
  out which keywords actually work.
- **No single-word keywords**, outside Google's own exceptions:
  "owned brand terms, medical conditions", and the list charity,
  charities, donate, donation, ngo, ngos, nonprofit, nonprofits,
  volunteer, volunteering. `creartbox` is an owned brand term, and
  `build_ads.py` refuses to write any other single-word keyword.
- **No overly generic keywords.** "music", "concerts", "composers"
  would all fail. Every keyword in the file is at least three words or
  a named thing.
- **Keywords with Quality Score 1 or 2 must go.** Google says to pause
  them with an automated rule. Check monthly.
- **Conversion-based bidding is mandatory** for accounts created on or
  after 22 April 2019: Maximize conversions, Maximize conversion
  values, Target CPA or Target ROAS. The campaigns use Maximize
  conversions. Whether it also lifts a **$2.00 maximum CPC** is
  *unverified*: no Google page I could read mentions a CPC cap at all.
  The ad groups carry a $2.00 max CPC, which is safe either way.
- **Structure:** Google's readable pages require only **two sitelinks**
  and geo-targeting. The two-ad-groups-per-campaign and
  two-ads-per-ad-group rules every consultant repeats are *unverified*.
  The files give every campaign two or more ad groups, a
  fifteen-headline responsive search ad per ad group, and four
  sitelinks; a second ad per ad group closes the question for free.
- **Geo-targeting is required.** Set per campaign in `1-campaigns.csv`,
  and set the campaign to "Presence", not "Presence or interest".
- **A programme survey**, sent "periodically" rather than annually,
  needs a thoughtful answer or the grant lapses.

---

## 3. The account

$329 a day is the grant ceiling. The split below adds up to it.

| Campaign | Daily | Targeting | Ad groups |
|---|---|---|---|
| CB \| Concerts \| New York | $170 | New York metro | Chamber music NYC · Classical concerts NYC · DiMenna Center · Winterlight, 11 December |
| CB \| Calls for Scores \| International | $70 | US, CA, UK, IE, AU, ES, DE, FR | Call for scores · Composer opportunities |
| CB \| Calls for Scores \| American | $60 | United States | American composers · US composition calls |
| CB \| Brand | $29 | US, ES, CA, UK | CreArtBox · Festival ADAR |

45 keywords, all phrase or exact. Landing pages are the ones built for
exactly these searches: `/classical-concerts-nyc.html` for the concert
queries, the two call pages for the composer queries.

**Grant accounts almost never spend the ceiling.** Do not read a low
spend as failure. The number that matters is applications and seats,
and after that the click-through rate that keeps the account alive.

---

## 4. Doing it

1. Confirm the grant is active at Google for Nonprofits, and that the
   Ads account is linked.
2. Install GA4 (section 1), then mark the three key events and import
   them as conversions in Google Ads.
3. Install **Google Ads Editor**, sign in, download the account.
4. Import `docs/ads/1-campaigns.csv` … `5-sitelinks.csv`, in that
   order. Editor will ask you to map columns; the headers are named
   the way it expects.
5. **Everything imports paused.** Read every ad on screen before
   enabling. The ads say things like "Tickets from $15" and "Friday 11
   December, 7:30pm": check each one is still true on the day you enable.
6. Add the negative keyword lists, the extra keywords and the second ad
   per ad group, and fix the settings the CSVs cannot carry (search
   partners, "Presence" targeting, auto-apply recommendations). All of
   that is in `docs/ads/BRIEF-google-ads-agent.md`.
7. Enable the brand campaign first, on its own, for a few days. It
   verifies the tracking end to end against real clicks, and its high
   click-through rate gives the account a cushion before the broader
   campaigns start.
8. Then enable the rest.

---

## 5. Keeping it alive

- **After every concert**, rewrite `DATED_HEADLINES` and
  `DATED_DESCRIPTIONS` in `build_ads.py` for the next date and
  re-import that one ad. On the morning of 12 December 2026 the
  Winterlight ad group is advertising a concert that has happened.
- **After 15 December 2026**, pause both calls campaigns and move
  their $130 a day to the concerts campaign.
- **Monthly:** check the account click-through rate is above 5%, pause
  any keyword at Quality Score 1 or 2, and look at the search terms
  report. Add anything irrelevant as a negative keyword; that single
  habit is what keeps the click-through rate up.
- **Yearly:** the programme survey.

---

## 6. What this is not

The grant pays for search ads only: no display, no video, no social.
It will not sell out a hall on its own, and for a concert six days away
a listing on Bachtrack or City Guide NY (see
`docs/external-listings.md`) reaches a more relevant audience than a
cold search ad does.

Where the grant earns its keep is the calls for scores. "Call for
scores 2026" is typed by exactly the people you want, all year, from
everywhere, and $20 a submission means those clicks pay for themselves
in a way concert tickets never quite do.
