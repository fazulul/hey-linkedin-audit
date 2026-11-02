---
name: hey-linkedin-audit
description: Hey Search's LinkedIn profile audit. Tests a profile with 25 evidence-based checks along the Visitor Path (Found, Understood, Believed, Contacted, Remembered), writes paste-ready copy with a source for every number, and builds a 10-page HTML report. Use for every LinkedIn audit. Trigger on "audit this LinkedIn", "LinkedIn audit", "Hey Linkedin Audit", "audit my profile", "score my LinkedIn", "rewrite my profile", "optimize my LinkedIn", or when a LinkedIn profile URL, screenshot or text is shared for review.
version: 3.0.0
category: Profile
---

# Hey Linkedin Audit

A profile is a path, not a list of sections. A visitor must find it, understand it, believe it, make contact and remember it. This audit finds where visitors drop off, and fixes that point first.

## Rules that never change

- **Goal first.** Every mark is judged against this person's goal and reader.
- **Evidence or nothing.** Every mark quotes something real. If you cannot see it, mark it `unknown`. Never guess.
- **No invented facts.** Every number in the new copy has a source in the proof ledger. The script stops if one does not.
- **Calculated, not claimed.** The script works out the score and the future scores. Do not write them by hand.
- **Fix the drop-off first.** Rank fixes by the stage where the most visitors are lost, then by effort.

## Step 1: Get the profile

With a LinkedIn URL, use the Apify actor `supreme_coder/linkedin-profile-scraper` with `findContacts: false`. The result has the photo and banner URLs. Featured and posts are usually missing, so mark those checks `unknown` unless you have a screenshot.

Without a URL, ask for a full-page screenshot or the pasted text.

## Step 2: Name the goal and the reader

Write one line for each:

- **Goal:** what the person wants, such as a job, clients or investors.
- **Reader:** who must act on the profile, such as a recruiter in one sector or a buyer in one market.
- **Search terms:** 4 to 8 words that reader types.

Find these in the profile. Ask one question only if you cannot.

## Step 3: Mark the 25 checks

Mark each check `pass`, `part`, `fail` or `unknown`. Evidence is 70 characters or fewer.

| Stage | ID | Pass means |
|---|---|---|
| Found | F1 | The headline has the role word the reader searches |
| | F2 | The headline names the sector or market |
| | F3 | The location fits the target market |
| | F4 | The top 3 skills match the search terms |
| | F5 | The current title uses searchable words |
| Understood | U1 | The first 100 headline characters say what they do. A phone may cut the rest |
| | U2 | The photo has a clear face and suits the reader |
| | U3 | The banner names the sector or offer |
| | U4 | The headline, banner and current role tell one story |
| | U5 | The About preview gives a reason to read on |
| Believed | B1 | There are at least 3 specific numbers |
| | B2 | The 2 latest relevant roles show results |
| | B3 | There are names the reader will recognise |
| | B4 | There are no blank roles or unexplained gaps |
| | B5 | There are no spelling, date or broken text errors |
| Contacted | C1 | The goal is visible on the first screen |
| | C2 | About ends with one clear ask |
| | C3 | Featured holds a proof or action item |
| | C4 | An easy contact route is set |
| | C5 | The profile URL is custom |
| Remembered | R1 | Posted in the last 30 days |
| | R2 | Posts are about the target topic |
| | R3 | Network size fits the experience level |
| | R4 | Recommendations from other people are visible |
| | R5 | There is a distinct point of view or story |

Scoring: pass 1, part 0.5, fail 0. Unknown checks are left out. Grades: S 90+, A 80+, B 70+, C 55+, D below 55.

## Step 4: Write the copy

**Proof ledger first.** List each number and named result, and where it came from. Status `pass` means it is in a role entry or the headline. Status `part` means the person must confirm it. Put every year and figure from the new copy in the ledger.

**Headline (3 options, 220 characters or fewer).** Put the reader's search word in the first 40 characters. Fit the core message in the first 100. Add one proof point. A job seeker keeps title and sector, because recruiters search by them. Someone who wants clients leads with the buyer and the result.

**About (2,600 characters or fewer, no bullets).** Keep this order:

1. The strongest named result, in the first line.
2. How this person's market really works, in words only an insider would use.
3. The career and the best names, as a short story.
4. The numbers.
5. One honest line that explains anything odd in the profile, such as a career change or a gap.
6. One clear ask, and who it is for.

**Experience.** Lead with results. Never add a figure the person did not give. If a role has no results, ask the person for them on the last page.

**Voice.** Write as this person would speak. Do not use em dashes. Do not use "passionate", "dedicated", "results-driven" or "In today's". Read it aloud. A generic sentence that any competitor could post gets rewritten.

**Posts.** Write 3 real first lines from this person's own material. Do not give a generic calendar.

## Step 5: Build the report

1. Save the photo and banner as JPEG next to a new `content.json`. Resize the photo to 300 px and the banner to 1000 px wide with `sips`.
2. Write `content.json`. Copy every field name from the example in `examples/`.
   - Most text fields hold HTML, so write `&amp;` for an ampersand. These are plain text: `headline.current`, `headline.options[].text`, `about.text`, `credibility.experience_text`, `ledger[].claim`.
   - In `roadmap.rows`, `fixes` lists the checks an action fully fixes. `helps` lists the checks that depend on time, other people or facts you have not seen. They count as partial, so the future score stays honest. Use at most 3 different `target` values.
   - Use the person's name or they/them unless their pronouns are stated. Paste-ready copy is in first person.
3. Run the script from this skill's folder. It stops with an error if a rule is broken:

```bash
python3 -I scripts/render_audit.py content.json site/index.html
```

4. Print to PDF and look at all 10 pages. Nothing may touch the footer. If a page overflows, shorten the copy.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=4000 --print-to-pdf=out.pdf "file://$PWD/site/index.html"
```

The 10 pages: cover, where visitors drop off, all 25 checks, the five-second test, found in search, proof ledger and About, Experience and Featured, posts and 30 days, roadmap with calculated scores, and items to confirm.

## Step 6: Deliver

Send `site/index.html` as a file. Then give the score, the weakest stage, the top 3 fixes, and what could not be seen.

Publish only when the user asks, and only to a place the user names.
