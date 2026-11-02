# Hey Linkedin Audit

A LinkedIn profile is a path, not a list of sections. A visitor must find it, understand it, believe it, make contact and remember it. This plugin finds where visitors drop off, and fixes that point first.

## What you get

- **25 checks with evidence.** Each is pass, partial, fail or not seen. Anything not visible is left out of the score, never guessed.
- **A proof ledger.** Every number in the new copy has a source. The build stops if one does not.
- **Paste-ready copy.** Three headlines, an About section, Experience entries and banner copy.
- **A calculated roadmap.** Future scores come from the checks each action fixes.
- **A 10-page HTML report** that also prints to A4.

## Install

```
/plugin install hey-linkedin-audit --marketplace fazulul/hey-linkedin-audit
```

## Use

Ask Claude to audit a LinkedIn profile, and share a URL, a screenshot or the pasted text.

## What it runs and sends

- A local Python script builds the report. It uses the standard library only and makes no network calls.
- With a URL, the skill can use the Apify actor `supreme_coder/linkedin-profile-scraper` if you have connected Apify. The profile URL goes to Apify.
- The finished report loads Google Fonts when opened. It holds a `noindex` tag.
- The plugin stores nothing and publishes nothing. Only audit a profile when you have a fair reason to review it.

## Test

```
python3 -I skills/hey-linkedin-audit/scripts/render_audit.py skills/hey-linkedin-audit/examples/example-profile.json /tmp/audit/index.html
```
