# Runbook: getting the campaigns running correctly

Written 10 November 2026, from the website side, for whoever is driving
the Google Ads account in a browser. Each numbered block is meant to be
pasted whole. Do them in order: later blocks assume the earlier ones.

The brief that built the account is `BRIEF-google-ads-agent.md`. This is
the part after it: turning a paused account into a working one.

**The clock.** Winterlight is 11 December, the two calls for scores close
on 15 December. That is 31 and 35 days from writing. Nothing here should
take more than four of them.

---

## 1. GA4: the three dimensions

The site sends three parameters on every tracked click. Without custom
dimensions they arrive, are stored, and never appear in a report.

| Parameter | Register it as | What it holds |
|---|---|---|
| `where` | Button placement | masthead, hero, body: which button was clicked |
| `production` | Concert | which concert, e.g. `tectonic-lullaby-2026` |
| `call` | Call for scores | which of the two calls |

All three are **event-scoped**.

`where` is the one that earns its keep. The site has four ticket buttons
on a concert page; without `where` they are one undifferentiated number,
and the question "does the masthead button sell anything, or do people
only buy from the body of the page" cannot be asked.

**A note on `production`.** It was called `event` until 10 November 2026.
In GA4, where every row and report is already an event, that was the one
name it could not have, so the site was changed. Register `production`.
If a parameter named `event` appears in the list, it is from before that
change and can be ignored.

---

## 2. Which conversions bid, and which only watch

Four things are tracked. They are not equally worth money.

| Action | In Google Ads | Why |
|---|---|---|
| `tickets` | **Primary**, count **One** | the outbound click to Eventbrite |
| `apply` | **Primary**, count **One**, value $20 | the application fee is $20 |
| `calendar` | **Secondary** | someone opening the season calendar is interested, not converting |
| `donate` | **Secondary** | real, but not what the grant is buying |

**Count "One", not "Every".** These fire on outbound clicks. Someone who
clicks the ticket button, comes back and clicks it again has not bought
twice, and "Every" would teach the bidding to chase hesitation.

**Secondary matters more than it sounds.** Only primary actions feed
Smart Bidding and the Conversions column. Leave `calendar` primary and
the Brand campaign, which uses the account default goal, will optimise
towards people opening a calendar rather than people buying a seat.

---

## 3. The order of switching on

Three gates first. None of them is optional.

1. **Advertiser verification is complete.** Pending verification can stop
   ads serving at all, and everything below assumes they serve.
2. **Both legacy campaigns are dealt with.** Read from the account on
   10 November 2026: there are six campaigns, not five.
   - **"Website traffic-Search-1", $500 a day, Maximize clicks, and it
     is ELIGIBLE.** It is what produced the 3 impressions, 1 click and
     $1.99 in the thirty days to 9 November. Pause it. The reason is not
     the money: an account created after 22 April 2019 must use
     conversion-based Smart bidding on every campaign, Maximize clicks
     is not on that list, and Google's own page says accounts in
     violation are "subject to automatic suspension without
     notification". Its ad also says "World class chamber concert",
     which is a superlative the site does not support.
   - **"Website traffic-Search-3", $300 a day, Maximize conversions,
     paused.** Not a violation while it is paused, but $300 a day of
     dormant budget is a hazard sitting next to a $329 ceiling. Decide
     deliberately whether it stays or goes.
3. **A real click has produced a conversion in Google Ads**, not just in
   GA4 realtime. Import takes hours. Until one has landed, Maximize
   conversions is bidding on nothing.

There is also **one draft campaign** in the account. Find out what it is
before switching anything on.

Then, and only then:

**Day 1 — Brand alone, $29.**
It cannot embarrass anyone, its click-through rate is the highest in the
account, and it proves the whole chain end to end against real traffic.
The account dates from May 2023, so there is no 90-day grace period: the
5% rule counts from the first month these campaigns run, and Brand is the
cushion. **Leave it on permanently.**

**Day 2 — both calls campaigns, $70 and $60.**
As soon as a conversion has landed. The original brief said wait three or
four days; that was written before the deadlines were this close. The
calls keywords are tight phrase and exact matches, so the CTR risk is
small, and 15 December is not negotiable. These are also the campaign
that pays for itself: $20 an application.

**Day 4 — concerts, $170.**
Last, because it has the loosest keywords and therefore the most CTR risk,
and because a concert in one city is the hardest thing here to sell with
cold search traffic. Watch its search terms report daily for the first
week and add negatives.

$329 a day in total, which is the grant ceiling.

**Expect the spend to be far below it.** 45 keywords, all phrase and
exact, in a narrow niche. The account will be limited by how many people
search these things, not by budget. Low spend is not failure; the numbers
that matter are applications, seats, and the click-through rate that
keeps the account alive.

---

## 4. The same week

- **Within 24 hours of each campaign going live, check for disapproved
  ads.** New ad copy gets flagged, and a disapproved ad is a silent ad.
- **Set the calls campaigns to end on 15 December 2026.** A campaign
  advertising a closed call is worse than one that needs switching back
  on, and the next cycle is a deliberate act anyway. Put a reminder
  somewhere that they are off.
- **Two automated rules:**
  - pause any keyword at Quality Score 1 or 2, weekly;
  - pause the "Winterlight, 11 December" ad group on 12 December 2026.
- **12 December:** that ad group is advertising a concert that happened
  last night. The rule should catch it; check that it did.
- **16 December:** both calls have closed. Their $130 a day moves to the
  concerts campaign.

---

## 5. The rejected sitelinks

Three of the four sitelinks were rejected. They are generated, so the fix
belongs in `docs/ads/build_ads.py` and not only in the account, or the
next import puts the rejected version straight back.

The four are: Season calendar, Coming to a concert, Open calls, About the
ensemble. All four point at pages that return 200, checked on
10 November, so a dead destination is not the reason.

**Send back the exact rejection reason for each one, as Google words it.**
Not a summary. The wording decides the fix, and the likely causes need
opposite remedies:

- *Destination mismatch*, if a sitelink points at the same page as the
  ad's own final URL. "Coming to a concert" goes to
  `classical-concerts-nyc.html`, which is also the final URL of three
  concert ad groups. If that is the reason, the sitelink needs a
  different destination, not different text.
- *Duplicate sitelinks*, because the same four are attached to all four
  campaigns. If that is it, they move to account level instead.
- Anything about the text itself, which is a copy fix.

Until they are fixed, the account is below the **two sitelink minimum**
the policy requires, which is itself a compliance failure.

---

## 6. What else to send back

- What the single **draft campaign** is.
- What the "Protect your account from unauthorized activity" notice wants.
- Any ad disapproval, with the reason, so the copy can be fixed at the
  source rather than only in the account.
