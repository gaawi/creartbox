# Brief: build the CreArtBox Google Ad Grant account

**For:** a Claude instance with access to the CreArtBox Google Ads account.
**From:** the Claude instance that has write access to the website repository
(`gaawi/creartbox`, live at https://creartbox.nyc). I have no Google
credentials, which is why this is a brief and not a pull request.
**Written:** 9 November 2026. Everything dated in here goes stale; check
section 3 against the live site before you write a single word of ad copy.

Read the whole thing before you touch the account. Sections 1 and 2 are
the ones that will get you in trouble if you skip them.

---

## 0. State of play, 9 November 2026, late evening

**The account has been built from this brief, and everything in it is
paused.** Nothing can spend. What follows is a record, not a plan.

Built: 4 campaigns, 10 ad groups, 45 keywords, 20 ads (two per ad group,
as section 9 asked), 16 sitelinks and the 4 shared negative lists, 147
terms. Search only, no search partners, no Display. Targeting set to
presence, not interest. Broad match, auto-created assets and AI Max all
off. All 21 auto-apply recommendation types turned off, which had been
adding keywords to the account on their own since 2023: **163 of them.**

Analytics: a GA4 property already existed, `G-VS5SK9S98C`, and it is now
linked to Google Ads. `tickets`, `apply` and `calendar` are conversions,
`apply` carrying a $20 value, which is the application fee. The concerts
campaign bids on `tickets`, both calls campaigns on `apply`, Brand on the
account default. The tag went onto the site the same evening and was
measured firing from the live site, so the property has data from now on.

Two findings worth carrying forward:

- **The account dates from May 2023**, so the 90-day CTR grace period in
  section 4 does not apply. The 5% rule counts from the first month these
  campaigns run.
- **Google's compliance guide, read from inside the account, confirms the
  structure rules I could not verify from outside:** two ad groups per
  campaign, two ads each, two sitelinks, one conversion a month. It still
  says nothing about a $2 CPC cap, and it says two months under 5% *can*
  lead to temporary deactivation, not *will*.

**Waiting on the owner, and only the owner can do them:**

1. **An old campaign, "Website traffic-Search-1", is still enabled at
   $500 a day.** It has not run since 2023, but it is enabled, it uses
   Maximize clicks, which this account is not allowed to use, and its ad
   says "World class chamber concert". It should be paused.
2. **Advertiser verification is pending.**
3. The decision to switch the new campaigns on at all.

---

## 1. Non-negotiables

1. **Nothing spends money without the owner saying so, in words, for that
   specific thing.** Build everything paused. Present a plan. Wait. The
   owner has an approval habit already: they expect to be shown a list and
   to say yes to it.
2. **Never invent a fact.** Section 3 is the complete set of claims you
   may make. If a headline needs a fact that is not in section 3, go and
   read the page on creartbox.nyc and quote it, or leave the headline out.
   Ad copy that promises something the site does not say is the one
   failure mode here that costs the organisation its reputation rather
   than just its money.
3. **Search only.** No Display, no Video, no Demand Gen. The owner asked
   for this explicitly: "no display". Performance Max is also out, both
   because of that instruction and because it would route spend into
   inventory nobody asked for.
4. **Every Final URL is on creartbox.nyc.** Never point an ad straight at
   Eventbrite or Tally. The ticket and application links live on the site's
   own pages, and that is also where the click tracking fires.
5. **Turn off auto-apply recommendations** before anything is enabled
   (Recommendations → auto-apply settings → uncheck everything). Google
   will otherwise quietly add broad-match keywords and widen targeting,
   and on a grant account that is what breaks the 5% CTR rule.
6. **Do not edit the website.** If a landing page needs a change, write it
   down and send it back; the repository is handled from the other side.

---

## 2. What this is for

CreArtBox is a chamber music ensemble in New York, founded 2013, a
501(c)(3) nonprofit. The grant is $10,000 a month of Google Search
inventory. Two things need to happen, and they both have a deadline:

| Goal | Deadline | Landing page |
|---|---|---|
| Sell seats for **Winterlight**, 11 December 2026 | 32 days from writing | `/concerts/tectonic-lullaby-2026.html` |
| Collect **paid applications** to two calls for scores, $20 each | 15 December 2026 | `/calls/scores-international.html`, `/calls/scores-american.html` |

The second is where a grant account actually earns its keep. "Call for
scores 2027" is typed, all year, from everywhere, by exactly the person
you want, and each application carries a $20 fee, so those clicks pay for
themselves in a way concert tickets never quite do. A concert four weeks
out, in one city, is a harder thing to sell with cold search traffic. Put
the effort where it converts, and do not read a low concert spend as
failure.

Grant accounts almost never spend the ceiling. The numbers that matter
are applications, seats, and after those the click-through rate that keeps
the account alive.

---

## 3. The verified fact sheet

**This is the complete set of claims permitted in ad copy.** Each one was
read off the live site on 9 November 2026.

**The organisation**
- CreArtBox. Founded in New York, 2013. A 501(c)(3) non-profit.
- Website: creartbox.nyc
- Four productions a season in New York, plus touring dates.
- Festival ADAR, in Asturias, Spain, is one of its projects.

**The New York venue**
- The DiMenna Center for Classical Music, 450 West 37th Street, between
  Ninth and Tenth Avenues, Midtown Manhattan.
- Concerts start at 7:30 pm.
- Subway: the A, C and E stop at 34th Street–Penn Station.
- **Do not name a hall inside the building.** The site does not say which
  one, and the DiMenna Center has several.

**Winterlight, the concert on sale**
- Friday 11 December 2026, 7:30 pm, at the venue above.
- Programme, in order:
  - Hannah Selin, *Tectonic Lullaby*, for piano quintet, 10 minutes, **world premiere**
  - Maurice Ravel, *Ma Mère l'Oye*, 17 minutes
  - Oliver Caplan, *Canciones de Monteverde*, for flute and string trio, 12 minutes, **winner of the open call**
  - Igor Stravinsky, *Petroushka*, chamber arrangement, 40 minutes
- Live visual projections are part of the programme.
- **Tickets from $15**, on sale through Eventbrite. The top of the range
  was $70 when the listing was read on 31 October 2026 — re-read the
  listing before quoting the top, and if in doubt say only "from $15".
- The site spells it **Petroushka**. Stravinsky's ballet is also widely
  spelled *Petrushka*. Both spellings need to be keywords.

**The two calls for scores**
- Both deadlines: 15 December 2026.
- $20 application fee. Two works per application. Any instrumentation,
  any age, any career stage.
- The first round is read blind.
- Selected works are played in the 2027/28 season.
- Eleven works in the current season arrived through this call.

**Things you may not say, because the site does not**
- Any hall name; any seat count; "limited seats"; "selling fast";
  "sold out"; "award-winning"; any prize or cash award attached to the
  calls (there is none — applicants pay a fee); any performer name beyond
  the four composers above; any press quote; any donation match.

---

## 4. Google's rules, and how much of this is actually verified

I tried to read Google's own pages. The **Ad Grants Policy Compliance
Guide itself would not load** — it returns navigation chrome and an empty
article body. So the list below is split into what I could quote and what
I could not. **Open the compliance guide yourself from inside the signed-in
account, where it will render, and check the unverified half before you
enable anything.**

### Quoted from Google's own pages

- **Click-through rate.** "Ad Grants accounts using Google Ads must
  maintain a 5% clickthrough rate (CTR) each month to remain eligible for
  the program." It is measured at account level, "not necessarily each
  keyword". "Failing to meet 5% CTR for two consecutive months will result
  in account deactivation." Reinstatement: pause the low-CTR keywords,
  get the "Total: filtered keywords" row to 5% or better for the last
  week, then request reinstatement.
  **A new account is not reviewed for this until it is 90 days old** —
  "Accounts will not be reviewed for this requirement until 90 days old."
  That is the window you have to find out which keywords actually work.
- **Smart bidding is mandatory.** Accounts created on or after 22 April
  2019 "must use conversion-based Smart bidding for all campaigns", which
  means Maximize conversions, Maximize conversion values, Target CPA or
  Target ROAS. Non-compliant campaigns are "subject to automatic bid
  strategy changes".
- **Conversion tracking is mandatory**, and the account must "accrue at
  least 1 conversion per month".
- **Single-word keywords** are "restricted except in cases of owned brand
  terms, medical conditions, basic keywords relating directly to
  supporting a charity". The listed exceptions are: charity, charities,
  donate, donation, ngo, ngos, nonprofit, nonprofits, volunteer,
  volunteering. Note that `creartbox` qualifies as an owned brand term,
  and that "terms with dashes, periods, or special characters are not
  treated as single-word keywords".
- **Overly generic keywords** are not permitted. Google's own examples of
  what fails: "best videos", "cool apps", "e-books", "today's news",
  "easy yoga", "download games", "things to do", "job alert", and the
  names of other organizations, places, historical events or people on
  their own. What passes: "museums in [your city name]".
- **Quality Score.** Keywords "with a Quality Score of 1 or 2" should be
  paused, and Google suggests doing it with an automated rule. The
  threshold is 1 or 2, not "below 3".
- **Mission-based advertising.** "Each ad and keyword in your Ad Grants
  account must reflect your organization's primary mission, be relevant to
  your nonprofit's programs and services."
- **Geo-targeting** and **at least 2 unique sitelink ad assets** are
  required. On Google's own readable pages these are the *only* structural
  minimums stated.
- **Enforcement is silent.** Keywords are paused "without notification",
  and accounts in violation are "subject to automatic suspension without
  notification".
- **The programme survey** is sent "periodically", not annually, and a
  "thoughtful response" is required to stay in the programme. (An earlier
  note of mine called it annual. That was wrong.)

### Not verified — confirm these in the account

- **The $2.00 maximum CPC bid**, and the widely repeated claim that
  conversion-based Smart bidding exempts an account from it. No Google
  page I could read mentions a CPC cap at all. The ad groups in the import
  files carry a $2.00 max CPC, which is safe under either reading, and
  Maximize conversions overrides it in practice anyway.
- **A minimum of 2 ad groups per campaign and 2 active ads per ad group.**
  Every consultant guide states this; no Google page I could read does.
  The structure below gives every campaign at least two ad groups anyway.
  For the ads, see section 9: build the second one. It costs nothing and
  it removes the question.
- Whether Performance Max is permitted or excluded from the CTR
  calculation. Irrelevant here — we are not running it.
- Any own-domain requirement for Final URLs. Irrelevant here — every URL
  is on creartbox.nyc by design.
- Any monthly login requirement. Log in monthly regardless; section 11
  gives you a reason to.

---

## 5. Analytics: done, and what is left in GA4

**The tag is installed and working.** `G-VS5SK9S98C` is live on all 140
indexable pages, written into the managed head block by
`tools/build_seo.py`, so no page can end up without it. Verified against
the live site with a real browser on 9 November 2026:

- loading `/concerts/tectonic-lullaby-2026.html` sends `page_view` to
  `G-VS5SK9S98C`;
- clicking a ticket button sends `en=tickets` with `ep.where=masthead`
  and `ep.event=tectonic-lullaby-2026`.

The `config` call is guarded by hostname, so only `creartbox.nyc` and
`www.creartbox.nyc` report. Pages opened from `127.0.0.1` while the site
is being built load the library and send nothing. Do not remove that
guard.

Four hooks exist in the site, via `data-cb-track` attributes that
`initConversions()` in `assets/site.js` forwards to `gtag`:
`tickets` (4 buttons), `apply` (5), `donate` (1), `calendar` (1). Every
one carries `page`, `href`, and where on the page it was clicked.

**What is left, and it is yours to do:**

1. In GA4, **mark `tickets` and `apply` as key events**. They will appear
   in Admin → Events once data has flowed; create them ahead of time if
   you do not want to wait.
2. **Register `where` and `event` as event-scoped custom dimensions**,
   or the parameters arrive but never show up in a report. Without
   `where` you cannot tell the masthead button from the hero button from
   the one in the body, which is the only thing that will tell you which
   placement actually sells a ticket.
3. **Link the GA4 property to Google Ads** (Admin → Product links, or
   Tools → Data manager on the Ads side) and import the key events as
   conversions.

Then section 6 for how to configure them.

---

## 6. The conversion actions

Three events will fire from the site once the tag is in. In GA4, mark them
as key events; in Google Ads, import them from GA4.

| Event | Fires on | Setting |
|---|---|---|
| `tickets` | a click on any ticket button | **Primary.** Count: **One** per click. No value. |
| `apply` | a click on Apply on either call page | **Primary.** Count: **One** per click. Value $20 if you want conversion value, since that is the fee. |
| `calendar` | opening the season calendar from the visitor guide | **Secondary.** Do not bid on it. |

Then set **campaign-level conversion goals** rather than leaving everything
on the account default:

- Concerts campaign → optimise for `tickets` only.
- Both calls campaigns → optimise for `apply` only.
- Brand campaign → account default is fine.

**Be honest with the owner about what these count.** They count people
leaving for the Eventbrite checkout or the Tally form, not people who
paid. Eventbrite and Tally hold the real numbers. Compare the two every
month and never conflate them: Google needs a conversion signal, the owner
needs the truth.

---

## 7. The account

Daily budgets add up to $329, which is the ceiling the $10,000 works out
to across a month.

| Campaign | Daily | Locations | Ad groups |
|---|---|---|---|
| `CB \| Concerts \| New York` | $170 | New York NY; Jersey City NJ | Chamber music NYC · Classical concerts NYC · DiMenna Center · Winterlight, 11 December |
| `CB \| Calls for Scores \| International` | $70 | US, CA, UK, IE, AU, ES, DE, FR | Call for scores · Composer opportunities |
| `CB \| Calls for Scores \| American` | $60 | United States | American composers · US composition calls |
| `CB \| Brand` | $29 | US, ES, CA, UK | CreArtBox · Festival ADAR |

45 keywords, phrase and exact match only. **No broad match anywhere.** On
a grant account broad match buys irrelevant clicks, and the click-through
rate is the thing the account lives or dies by.

### Settings the import files cannot carry — set these by hand

- **Networks:** Google Search only. **Uncheck "Include Google search
  partners"** and make sure the Display Network is off. Search partners
  dilute CTR and the grant does not need them.
- **Location options:** set targeting to **"Presence: People in or
  regularly in your targeted locations"**, not the default "Presence or
  interest". The default serves ads to people merely *searching about*
  New York from anywhere, and it is the most common reason a grant
  account's CTR collapses.
- **Language:** English. The site is in English.
- **Ad rotation:** leave on optimise.
- **Automatically created assets:** off, at account level. It writes
  headlines from page content and it will put claims in your ads that
  section 3 does not allow.
- **Dynamic Search Ads:** off.
- **Bid strategy:** Maximize conversions, with **no target CPA** at first.
  Add a target only once there are 30-ish conversions a month to learn
  from, which may well be never on this budget.
- **Ad schedule:** all hours. Do not try to be clever before there is data.

---

## 8. The import files

Written and character-checked by `docs/ads/build_ads.py`, in the order
Google Ads Editor wants them. The repository is public, so fetch them
directly:

```
https://raw.githubusercontent.com/gaawi/creartbox/main/docs/ads/1-campaigns.csv
https://raw.githubusercontent.com/gaawi/creartbox/main/docs/ads/2-ad-groups.csv
https://raw.githubusercontent.com/gaawi/creartbox/main/docs/ads/3-keywords.csv
https://raw.githubusercontent.com/gaawi/creartbox/main/docs/ads/4-ads.csv
https://raw.githubusercontent.com/gaawi/creartbox/main/docs/ads/5-sitelinks.csv
https://raw.githubusercontent.com/gaawi/creartbox/main/docs/ads/6-negatives.csv
https://raw.githubusercontent.com/gaawi/creartbox/main/docs/ads/6-negatives.txt
https://raw.githubusercontent.com/gaawi/creartbox/main/docs/ads/build_ads.py
```

4 campaigns, 10 ad groups, 45 keywords, 10 responsive search ads, 16
sitelink rows, 147 negative terms. Every headline, description and
sitelink is inside Google's limits (30 / 90 / 25 / 35 characters) because
the generator refuses to write one that is not, and it refuses to write a
single-word keyword that is not the brand name. Import 1 to 5 in order;
the column headers are named the way Editor expects. **Everything imports
paused.**

`6-negatives.csv` is the same data as campaign-level negatives, with a
`Criterion Type` column of `Negative Broad` or `Negative Phrase`. If
Editor will not map those headers, use `6-negatives.txt` instead: it is
the four lists as plain text with a comment line naming the campaigns each
one applies to, and the web interface takes a pasted list straight into a
shared negative list. Shared lists are the better home for them — one edit
then reaches every campaign.

---

## 9. The second ad in each ad group

Build a second responsive search ad per ad group. Whether Google strictly
requires it is the one thing I could not confirm (section 4), it raises Ad
Strength either way, and it gives the system something to rotate against.

**Reordering the same fifteen headlines is not a second ad.** Write one
that takes a different angle, drawing only on section 3:

- **Concerts ad groups.** The first ad sells the series. Make the second
  one practical — the things somebody deciding whether to come actually
  wants: the street, the cross-streets, the subway, the 7:30 start, that
  tickets begin at $15. "450 West 37th Street", "Ninth and Tenth Avenues",
  "A, C and E to Penn Station", "Doors at 7:30 pm".
- **DiMenna Center ad group** specifically: see the negatives in section 10
  before you write anything here. Most people searching that name are
  musicians looking to rent rehearsal space, not audience.
- **Calls ad groups.** The first ad states the terms. Make the second one
  about what happens to a score: read blind in the first round, read by
  the five musicians who would play it, played in New York in the 2027/28
  season, eleven works in the current season arrived this way.
- **Winterlight ad group.** The first ad leads on Stravinsky and Ravel.
  Lead the second on the two living composers: a world premiere by Hannah
  Selin, and Oliver Caplan's piece chosen through the open call. Keep
  "From $15" and "Friday 11 December" in both.
- **Brand ad groups.** Ten headlines is plenty; do not pad. For Festival
  ADAR, name Asturias so the ad self-selects against the Hebrew month of
  the same name (section 10).

Pin nothing except, in the Winterlight ad, the date headline to position 1
if you want it always shown. Pinning more than that throws away the only
thing responsive search ads are good at.

---

## 10. Negative keywords

This is the part that keeps the 5% CTR alive. The terms are in
`6-negatives.txt` and `6-negatives.csv` (section 8); build them as **shared
lists** under Tools → Shared library, so one edit reaches every campaign.
Four lists, 147 terms. What each is for, and why, because you will have to
judge the ones I could not foresee:

**`CB | Never`, on all four campaigns.** Free and pirated files, jobs,
lessons and degrees, reference lookups, private hire and instrument
retail, bargain hunting. None of it is an audience and none of it is a
composer.

**`CB | Not an audience`, on the concerts campaign.** Two thirds of this
list is rehearsal space, and that is the single most valuable block in the
account: **the DiMenna Center's own main business is renting rehearsal and
recording rooms**, so most of the search volume on its name is musicians
looking to book one, not an audience looking for a ticket. Without
`rehearsal`, `studio`, `rent`, `booking`, `hourly`, `rates` and the rest,
the DiMenna ad group spends its budget at a CTR that will take the whole
account under 5%. The remainder is other halls (Carnegie, Lincoln Center,
the 92nd Street Y and so on — somebody searching those wants those) and
other genres.

**`CB | Not a composer`, on both calls campaigns.** The first block is
sport and standardised tests, which is the real hazard in any query
containing the word *score*: `football`, `live score`, `credit score`,
`sat scores`. The second is fee-averse and prize-seeking intent, because
this call **charges $20 and awards no money** — `no entry fee`,
`cash prize`, `prize money`, `scholarship`. Someone looking for a free
competition with a cash prize will click, read, and leave, which is the
worst possible outcome for both CTR and the owner's hosting bill. The
third is the wrong field entirely: film, games, library and production
music.

**`CB | Brand noise`, on the brand campaign.** Account-login and
complaints queries, plus the Hebrew calendar: **Adar is a month in the
Jewish year**, so "festival adar" collects Purim and Rosh Chodesh traffic
that has nothing to do with Asturias. Naming Asturias in the ad copy helps
too.

Add to these every week from the search terms report. That habit, more
than anything in this brief, is what keeps the account alive.

---

## 11. Launch sequence

1. Confirm the grant is active in Google for Nonprofits and the Ads
   account is linked. Note the account creation date: it decides whether
   the 22 April 2019 Smart-bidding rule applies, and when the 90-day CTR
   grace period ends.
2. Finish the GA4 side (section 5): key events, the two custom
   dimensions, and the link to Ads. Watch a real click land in GA4
   realtime before you believe any of it.
3. Import the conversions into Google Ads and set the campaign-level goals
   (section 6).
4. Import the CSVs, paused. Build the negative lists (section 10), write
   the second ad per ad group (section 9), and fix every setting in
   section 7 by hand.
5. **Read every ad on screen.** Each one claims a date, a price or a
   deadline. Check each against the live site that day. The Winterlight ad
   is wrong the morning of 12 December.
6. **Enable the brand campaign alone, for three or four days.** It proves
   the tracking end to end against real clicks, it cannot embarrass anyone,
   and its high CTR gives the account a cushion before anything broader
   starts.
7. Send the owner the list of what is about to go live, with the daily
   budgets, and wait for a yes.
8. Then enable the calls campaigns. Then the concerts campaign.

---

## 12. Keeping it alive

**Weekly, while Winterlight is on sale**
- Search terms report. Add every irrelevant query as a negative. This one
  habit is most of what keeps CTR above 5%.
- Check the Winterlight ad still matches the ticket page.

**Monthly**
- Account CTR above 5%. If a month comes in under, fix it that week; two
  consecutive months is deactivation.
- Pause every keyword at Quality Score 1 or 2. An automated rule will do
  it, and Google suggests exactly that.
- At least one conversion recorded. Zero conversions in a month is a
  compliance failure, not just a bad month.
- Log in. There is a login expectation and it costs nothing to satisfy.

**On these dates**
- **12 December 2026:** the Winterlight ad is advertising a concert that
  has happened. Pause that ad group the morning after, and tell the owner
  so the next one can be written. In the repository, the copy lives in
  `DATED_HEADLINES` and `DATED_DESCRIPTIONS` in `docs/ads/build_ads.py`.
- **16 December 2026:** both calls have closed. Pause both calls campaigns
  and move their $130 a day to the concerts campaign. Reopen them when the
  next cycle opens.
- **The rest of the season.** The New York Series at the DiMenna Center
  continues with **Pressure and Release on 23 April 2027** and
  **Feverdream on 7 May 2027**. Ask for the programmes when they go on
  sale, and build an ad group for each the way the Winterlight one works.
  Everything else on the calendar is touring and is not ours to sell:
  Louisville on 28 February, Saugerties on 18 April, Festival ADAR in
  August, Gettysburg on 28 September, The Chapel Restoration on 17
  October. The presenter sells those seats, so no ad group and no
  ticket keywords for them.
  (An earlier draft of this section said the season continued on 28
  February and 23 April. 28 February is the Louisville date. Corrected
  after the live calendar was read event by event.)

---

## 13. What to send back

Write the owner a short list, not an essay. They read on a phone.

1. Confirmation that the key events, the two custom dimensions and the
   GA4-to-Ads link are in place, since nothing can be optimised before
   they are.
2. Account creation date, and therefore when the 90-day CTR grace period
   ends.
3. Whether the compliance guide, read from inside the account, confirms or
   contradicts anything in section 4 — above all the $2 CPC cap and the
   two-ads-per-ad-group rule.
4. Anything in section 3 you could not reconcile with the live site.
5. The exact list of campaigns, budgets and dates you are asking
   permission to enable.

And if something in this brief is wrong, say so plainly. It was written
without ever seeing the account.
