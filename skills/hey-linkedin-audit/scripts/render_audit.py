#!/usr/bin/env python3
"""Render a Hey Search LinkedIn audit: the 25-check Visitor Path report.

Usage: render_audit.py content.json out/index.html
Image paths in the JSON are relative to the JSON file. Field names: see the example in examples/.
Exits non-zero if a self-check fails, so a broken report cannot be published by accident.
"""
import base64, html, json, os, re, sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'assets')
TOTAL = 10
MARKS = {'pass': 1, 'part': .5, 'fail': 0, 'unknown': None}
MARK_TEXT = {'pass': 'PASS', 'part': 'PARTIAL', 'fail': 'FAIL', 'unknown': 'NOT SEEN'}
STAGES = [
    ('F', 'Found', 'Do the right people find this profile?', [
        ('F1', 'Headline has the role word the reader searches'),
        ('F2', 'Headline names the sector or market'),
        ('F3', 'Location fits the target market'),
        ('F4', 'Top 3 skills match the search terms'),
        ('F5', 'Current title uses searchable words')]),
    ('U', 'Understood', 'Does a stranger get it in 5 seconds?', [
        ('U1', 'First 100 headline characters say what they do'),
        ('U2', 'Photo: clear face, right for the reader'),
        ('U3', 'Banner names the sector or offer'),
        ('U4', 'Headline, banner and current role tell one story'),
        ('U5', 'About preview gives a reason to read on')]),
    ('B', 'Believed', 'Is there proof behind the claims?', [
        ('B1', 'At least 3 specific numbers'),
        ('B2', 'The 2 latest relevant roles show results'),
        ('B3', 'Names the reader will recognise'),
        ('B4', 'No blank roles or unexplained gaps'),
        ('B5', 'No spelling, date or broken text errors')]),
    ('C', 'Contacted', 'Is the next step obvious?', [
        ('C1', 'The goal is visible on the first screen'),
        ('C2', 'About ends with one clear ask'),
        ('C3', 'Featured holds a proof or action item'),
        ('C4', 'An easy contact route is set'),
        ('C5', 'Custom profile URL')]),
    ('R', 'Remembered', 'Will they think of this person later?', [
        ('R1', 'Posted in the last 30 days'),
        ('R2', 'Posts are about the target topic'),
        ('R3', 'Network size fits the experience level'),
        ('R4', 'Recommendations from others'),
        ('R5', 'A distinct point of view or story')]),
]
CHECK_IDS = [cid for s in STAGES for cid, _ in s[3]]
ESC = html.escape


def data_uri(path):
    mime = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def plain(text):
    """Paste-ready copy: plain text in the JSON, line breaks kept."""
    return ESC(text.strip(), quote=False).replace('\n', '<br>')


def grade(score):
    return 'S' if score >= 90 else 'A' if score >= 80 else 'B' if score >= 70 else 'C' if score >= 55 else 'D'


def tally(values):
    """values: check id -> 1, .5, 0 or None. Unknown checks are left out, never counted as 0."""
    known = [v for v in values.values() if v is not None]
    earned = sum(known)
    return earned, len(known), (round(earned / len(known) * 100) if known else None)


def score_path(values, rows):
    """Score after each roadmap target, from the checks each action fixes."""
    now, path = dict(values), []
    for target in dict.fromkeys(r['target'] for r in rows):
        for r in rows:
            if r['target'] == target:
                now.update({cid: 1 for cid in r['fixes']})
                now.update({cid: max(now.get(cid) or 0, .5) for cid in r.get('helps', [])})
        path.append((target, tally(now)[2]))
    return path


def action_checks(row):
    parts = []
    if row['fixes']:
        parts.append('Fixes ' + ', '.join(row['fixes']))
    if row.get('helps'):
        parts.append('Helps ' + ', '.join(row['helps']))
    return ' · '.join(parts)


def phone_cut(text):
    return text if len(text) <= 100 else text[:100].rstrip() + '...'


def numbers(text):
    return set(re.findall(r'\d[\d,.]*\d|\d', text))


def render(c, base):
    logo = data_uri(os.path.join(ASSETS, 'hey-search-logo.png'))
    css = open(os.path.join(ASSETS, 'report.css'), encoding='utf-8').read()
    checks = c['checks']
    assert sorted(checks) == sorted(CHECK_IDS), 'checks must hold all 25 ids'
    values = {k: MARKS[v['mark']] for k, v in checks.items()}
    earned, known, score = tally(values)
    passed = sum(1 for v in checks.values() if v['mark'] == 'pass')
    unseen = 25 - known
    name, date, ver = c['name'], c['date'], c.get('version', 'V1')

    def foot(n):
        return (f'<footer class="foot"><span>HEY SEARCH &nbsp; · &nbsp; PREPARED FOR {ESC(name.upper())}</span>'
                f'<span>{date} <b>{n:02d} / {TOTAL:02d}</b></span></footer>')

    def sheet(n, sid, eyebrow, title, em, body):
        return (f'<section class="sheet" id="section-{sid}"><header class="page-head"><div class="brandline">'
                f'<img src="{logo}" alt="Hey Search"><span>THE VISITOR PATH AUDIT</span></div>'
                f'<div class="page-head-right">AUDIT  /  {ver}</div></header><div class="eyebrow">{eyebrow}</div>'
                f'<h2 class="page-title">{title} <em>{em}</em></h2>\n{body}{foot(n)}</section>\n')

    def stage_pct(s):
        return tally({cid: values[cid] for cid, _ in s[3]})[2]

    def stage_tag(letter):
        s = next(x for x in STAGES if x[0] == letter)
        pct = stage_pct(s)
        return f'<div class="score-tag">{s[1].upper()} &nbsp; <span>{ESC(s[2])}</span><b>{"NOT SEEN" if pct is None else str(pct) + "%"}</b></div>'

    # 1 Cover
    frac = score / 100 * 326.73
    cover = (f'<section class="sheet" id="section-1"><div class="cover-glow"></div><div class="cover-header"><img src="{logo}" alt="Hey Search"><span>PRIVATE PROFILE REVIEW · {ver}</span></div>'
             f'<div class="cover-content"><div class="micro-label"><b></b> HEY SEARCH / THE VISITOR PATH AUDIT</div>'
             f'<h1>{ESC(name)}<span class="line-2">LinkedIn <em>Audit.</em></span></h1><p class="cover-intro">{c["cover_intro"]}</p>'
             f'<div class="hero-stat"><div class="hero-number">{score}<span>/100</span></div><div class="hero-grade"><strong>{"<br>".join(c["verdict"])}</strong><small>Grade {grade(score)} · {known} of 25 checks visible</small></div>'
             f'<div class="big-circle"><svg viewBox="0 0 120 120" role="img" aria-label="Score {score} percent"><circle cx="60" cy="60" r="52" fill="none" stroke="#3A3A3E" stroke-width="10"/><circle cx="60" cy="60" r="52" fill="none" stroke="#FF5474" stroke-width="10" stroke-linecap="round" stroke-dasharray="{frac:.2f} {326.73 - frac:.2f}" transform="rotate(-90 60 60)"/><text x="60" y="69" text-anchor="middle" font-family="Space Grotesk,Poppins,sans-serif" font-weight="700" font-size="26" fill="#FFB0C0">{score}%</text></svg></div></div>'
             f'<div class="cover-details"><div><span>THE GOAL WE SCORED AGAINST</span><strong>{c["goal"]}</strong></div><div><span>REVIEW DATE</span><strong>{date}</strong></div><div><span>PROFILE</span><strong>{ESC(c["profile_url"])}</strong></div></div></div>'
             f'<div class="cover-end">Editorial audit based on {c["source_short"]}. Not a score issued by LinkedIn.</div>{foot(1)}</section>\n')

    # 2 Diagnosis
    rows, weakest = '', None
    for i, s in enumerate(STAGES, 1):
        pct = stage_pct(s)
        if pct is not None and (weakest is None or pct < weakest[1]):
            weakest = (s[1], pct)
        shown = '<strong>n/a</strong>' if pct is None else f'<strong>{pct}<small>%</small></strong>'
        rows += f'<div class="score-row"><span class="index">{i:02d}</span><span class="s-name">{s[1]}<small>{ESC(s[2])}</small></span><div class="meter"><i style="width:{pct or 0}%"></i></div>{shown}</div>\n'
    method = f'Method: each check is pass (1), partial (0.5) or fail (0). {num(earned)} points from {known} visible checks = {score}/100.'
    if unseen:
        method += f' {unseen} checks were not visible, so they are left out, not guessed.'
    pri = ''.join(f'<div class="panel{" danger-panel" if i == 0 else ""}"><span class="pill-hot">{i + 1:02d} · {p["tag"]}</span><h3>{p["title"]}</h3><p>{p["text"]}</p></div>' for i, p in enumerate(c['priorities']))
    diagnosis = sheet(2, 2, '01 / WHERE VISITORS DROP OFF', c['overview']['title'], c['overview']['em'],
                      f'<p class="lede">{c["overview"]["lede"]}</p><div class="three-metrics"><div><div class="metric-val">{score}<span>/100</span></div><small>VISITOR PATH SCORE</small></div><div><div class="metric-val">{passed}<span>/{known}</span></div><small>VISIBLE CHECKS PASSED</small></div><div><div class="metric-val">{weakest[1]}<span>%</span></div><small>WEAKEST STAGE: {weakest[0].upper()}</small></div></div>'
                      f'<div class="two-col"><div class="panel tight"><div class="panel-head">THE FIVE STAGES OF A VISIT</div>{rows}<div class="tiny-note">{method} The next page shows every check and its evidence.</div></div><div class="right-stack">{pri}</div></div>')

    # 3 All 25 checks
    table = ''
    for s in STAGES:
        pct = stage_pct(s)
        table += f'<div class="check-stage"><span>{s[1].upper()}</span><span>{"NOT SEEN" if pct is None else str(pct) + "%"}</span></div>'
        for cid, label in s[3]:
            v = checks[cid]
            table += f'<div class="check-row"><b>{cid}</b><span>{label}</span><span class="check-ev">{v["evidence"]}</span><span class="mark mark-{v["mark"]}">{MARK_TEXT[v["mark"]]}</span></div>'
    evidence = sheet(3, 'checks', '02 / THE EVIDENCE', 'All 25 checks.', 'Nothing hidden.', f'<div class="check-table">{table}</div>')

    # 4 Understood
    v, p, b = c['visual'], c['visual']['photo'], c['visual']['banner']
    visual = sheet(4, 3, '03 / THE FIVE-SECOND TEST', v['title'], v['em'],
                   f'<div class="compare-box"><div><small>WHAT A STRANGER CONCLUDES TODAY</small><p>{v["concludes"]}</p></div><div><small>WHAT THEY SHOULD CONCLUDE</small><p>{v["should"]}</p></div></div>'
                   f'<div class="split-audit"><div class="audit-block photo-audit-v3"><div class="audit-top"><span>U2 / PROFILE PHOTO</span><strong>{MARK_TEXT[checks["U2"]["mark"]]}</strong></div><h3>{p["heading"]}</h3>'
                   f'<div class="profile-photo-evidence"><div class="profile-photo-frame"><img alt="Current LinkedIn profile photo of {ESC(name)}" src="{data_uri(os.path.join(base, p["image"]))}"><span class="photo-stamp">CURRENT PHOTO</span></div><div class="photo-verdict"><b>{p["verdict"]}</b><p>{p["text"]}</p></div></div>'
                   f'<div class="action-label">WHAT TO DO</div><p class="action-copy">{p["recommendation"]}</p></div>'
                   f'<div class="audit-block"><div class="audit-top"><span>U3 / PROFILE BANNER</span><strong>{MARK_TEXT[checks["U3"]["mark"]]}</strong></div><h3>{b["heading"]}</h3><p>{b["text"]}</p>'
                   f'<div class="banner-compare"><figure class="banner-shot"><label>EXISTING COVER · FROM LINKEDIN</label><img alt="Current LinkedIn cover image of {ESC(name)}" src="{data_uri(os.path.join(base, b["image"]))}"></figure><div class="banner-new"><label>PROPOSED COVER COPY</label><b style="font-size:13px">{b["new_line"]}</b><small>{b["new_small"]}</small></div></div>'
                   f'<div class="action-label">DESIGN BRIEF</div><p class="action-copy">{b["brief"]}</p></div></div>')

    # 5 Found
    h = c['headline']
    current = h['current'].lower()
    terms = ''.join(f'<span class="term {"term-ok" if t.lower() in current else "term-miss"}">{ESC(t)}</span>' for t in h['search_terms'])
    choices = ''
    for i, o in enumerate(h['options']):
        letter = 'abc'[i]
        choices += (f'<div class="choice{" selected" if i == 0 else ""}"><div class="choice-head"><b>OPTION {letter.upper()} · {o["label"]}</b><span>{len(o["text"])} characters</span></div>'
                    f'<p id="headline-{letter}">{plain(o["text"])}</p><button class="copy-btn" data-copy="headline-{letter}">Copy headline</button></div>')
    found = sheet(5, 4, '04 / FOUND IN SEARCH', h['title'], h['em'],
                  stage_tag('F') + f'<div class="compare-box"><div><small>A PHONE SHOWS ONLY THIS</small><p>{ESC(phone_cut(h["current"]), quote=False)}</p></div><div><small>WORDS THE READER SEARCHES: IN THE HEADLINE TODAY?</small><p class="terms">{terms}</p></div></div>'
                  f'<div class="choices">{choices}</div><div class="bottom-insight"><b>Why option A:</b> {h["why_a"]}</div>')

    # 6 Believed
    a = c['about']
    ledger = ''.join(f'<div class="ledger-row"><span>{ESC(x["claim"], quote=False)}</span><span class="check-ev">{x["source"]}</span><span class="mark mark-{x["status"]}">{"CONFIRM" if x["status"] == "part" else "SOURCED"}</span></div>' for x in c['ledger'])
    about = sheet(6, 5, '05 / BELIEVED', a['title'], a['em'],
                  stage_tag('B') + f'<div class="panel ledger"><div class="panel-head">THE PROOF LEDGER: EVERY NUMBER IN THE NEW COPY HAS A SOURCE</div>{ledger}</div>'
                  f'<div class="paste-block"><div class="paste-header"><b>ABOUT SECTION · PASTE-READY</b><button class="copy-btn" data-copy="about-final">Copy About</button></div><div class="paste-body" id="about-final">{plain(a["text"])}</div></div>')

    # 7 Contacted
    cr = c['credibility']
    feat = ''.join(f'<li>{x}</li>' for x in cr['featured'])
    exp = ''.join(f'<li>{x}</li>' for x in cr['experience_fixes'])
    skills = ''.join(f'<span>{x}</span>' for x in cr['skills'])
    cred = sheet(7, 6, '06 / CONTACTED', cr['title'], cr['em'],
                 f'<div class="cred-grid"><div class="panel"><div class="section-score"><span>C3 / FEATURED</span><strong>{MARK_TEXT[checks["C3"]["mark"]]}</strong></div><h3>{cr["featured_heading"]}</h3><ol class="numbered">{feat}</ol></div>'
                 f'<div class="panel"><div class="section-score"><span>B2, B4, B5 / EXPERIENCE</span></div><h3>{cr["experience_heading"]}</h3><ul class="cross-list">{exp}</ul></div></div>'
                 f'<div class="paste-block shorter"><div class="paste-header"><b>EXPERIENCE · PASTE-READY</b><button class="copy-btn" data-copy="experience-final">Copy text</button></div><div class="paste-body" id="experience-final">{plain(cr["experience_text"])}</div></div>'
                 f'<div class="panel slim"><div class="section-score"><span>F4 / TOP SKILLS</span><strong>{MARK_TEXT[checks["F4"]["mark"]]}</strong></div><div class="skills-row">{skills}</div><p class="fine">{cr["skills_note"]}</p></div>')

    # 8 Remembered
    ct = c['content']
    posts = ''.join(f'<div><span>POST {i}</span><b>{x["hook"]}</b><p>{x["why"]}</p><small>{x["tag"]}</small></div>' for i, x in enumerate(ct['posts'], 1))
    weeks = ''.join(f'<div><b>WEEK {i}</b><p>{w}</p></div>' for i, w in enumerate(ct['weeks'], 1))
    content = sheet(8, 7, '07 / REMEMBERED', ct['title'], ct['em'],
                    stage_tag('R') + f'<p class="lede">{ct["lede"]}</p><div class="rhythm">{posts}</div><div class="panel"><div class="panel-head">FIRST 30 DAYS</div><div class="timeline">{weeks}</div></div>')

    # 9 Roadmap
    r = c['roadmap']
    actions = ''.join(f'<div class="action-row"><b>{x["priority"]}</b><span><strong>{x["title"]}</strong><small>{x["detail"]} · {action_checks(x)}</small></span><span>{x["owner"]}</span><span>{x["target"]}</span></div>' for x in r['rows'])
    path = f'<div><b>{score}<em>{grade(score)}</em></b><small>TODAY</small></div>' + ''.join(f'<div><b>{s}<em>{grade(s)}</em></b><small>AFTER {t.upper()}</small></div>' for t, s in score_path(values, r['rows']))
    roadmap = sheet(9, 8, '08 / EXECUTION', r['title'], r['em'],
                    f'<div class="action-table"><div class="action-head"><span>PRIORITY</span><span>WHAT TO DO</span><span>OWNER</span><span>TARGET</span></div>{actions}</div><div class="score-path">{path}</div>'
                    f'<p class="tiny-note">These scores are calculated from the checks each action fixes. They are targets, not a promise.</p>'
                    f'<div class="two-col compact"><div class="panel"><div class="panel-head">SUCCESS IS NOT JUST A BIGGER SCORE</div><p>{r["success"]}</p></div><div class="panel"><div class="panel-head">WHAT THIS REPORT GIVES</div><p>{r["delivers"]}</p></div></div>')

    # 10 Confirm
    nx = c['next']
    items = ''.join(f'<div><span>{i:02d}</span><div><b>{x["title"]}</b><p>{x["text"]}</p></div><small>{x["tag"]}</small></div>' for i, x in enumerate(nx['checks'], 1))
    cta = nx['cta']
    next_step = sheet(10, 9, '09 / NEXT STEP', nx['title'], nx['em'],
                      f'<p class="lede">{nx["lede"]}</p><div class="checklist">{items}</div><div class="methodology"><b>ABOUT THIS ASSESSMENT</b><p>{nx["assessment"]} {method} All marks are editorial judgments, not LinkedIn metrics.</p></div>'
                      f'<div class="last-cta"><div><span>HEY SEARCH · GROW THROUGH CLARITY</span><h3>{cta["title"]}</h3><p>{cta["text"]}</p></div><div><a class="link-btn" href="{cta["url"]}">{cta["label"]}</a></div></div>')

    script = "document.querySelectorAll('.copy-btn').forEach(btn=>{btn.addEventListener('click',async()=>{let el=document.getElementById(btn.dataset.copy);if(!el)return;let t=el.innerText.trim();try{await navigator.clipboard.writeText(t);let old=btn.textContent;btn.textContent='Copied';setTimeout(()=>btn.textContent=old,1800)}catch(err){window.prompt('Copy this text:',t)}})});"
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0D0A0B">'
            f'<title>Hey Search | {ESC(name)} · LinkedIn Audit ({ver})</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet"><style>\n{css}</style></head><body>'
            f'<div class="site-nav"><a href="#section-1" aria-label="Hey Search audit home"><img src="{logo}" alt="Hey Search"></a><div class="links"><a href="#section-2">Score</a><a href="#section-checks">Checks</a><a href="#section-4">Copy</a><a href="#section-8">Roadmap</a><button type="button" onclick="window.print()">Print / PDF</button></div></div>'
            f'<main>{cover}{diagnosis}{evidence}{visual}{found}{about}{cred}{content}{roadmap}{next_step}</main><script>{script}</script></body></html>')


def num(n):
    return f'{n:g}'


class Balance(HTMLParser):
    VOID = {'meta', 'link', 'img', 'br', 'circle'}

    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag not in self.VOID and (not self.stack or self.stack.pop() != tag):
            self.errors.append(f'{tag} at line {self.getpos()[0]}')


def check(doc, c):
    """Fails loudly if the report breaks a format rule."""
    text = re.sub(r'data:image/[a-z]+;base64,[A-Za-z0-9+/=]+', '', doc)
    assert '—' not in text, 'em dash in report'
    assert doc.count('class="sheet"') == TOTAL, f'report must have {TOTAL} sheets'
    assert doc.count('name="robots" content="noindex,nofollow"') == 1, 'report must be noindex'
    assert not re.search(r'\[[A-Z_]{3,}\]|\bTODO\b', text), 'placeholder left'
    options = c['headline']['options']
    assert len(options) == 3 and all(len(o['text']) <= 220 for o in options), 'need 3 headlines under 220 characters'
    assert len(c['about']['text']) <= 2600, 'About is over the LinkedIn limit'
    assert '\n- ' not in c['about']['text'], 'no bullets in the About rewrite'
    assert len(c['priorities']) == 3, 'need 3 priorities'
    for cid, v in c['checks'].items():
        assert len(v['evidence']) <= 70, f'{cid} evidence is over 70 characters'
    for r in c['roadmap']['rows']:
        assert set(r['fixes']) | set(r.get('helps', [])) <= set(CHECK_IDS), f'unknown check in {r["title"]}'
    assert len(set(r['target'] for r in c['roadmap']['rows'])) <= 3, 'roadmap allows 3 targets'
    # The truth rule: every number in the paste-ready copy must have a source in the ledger.
    ledger = ' '.join(x['claim'] + ' ' + x['source'] for x in c['ledger'])
    copy = ' '.join([o['text'] for o in options] + [c['about']['text'], c['credibility']['experience_text']])
    missing = numbers(copy) - numbers(ledger)
    assert not missing, f'numbers with no source in the ledger: {sorted(missing)}'
    # Logic checks
    assert tally({'a': 1, 'b': 0, 'c': None})[2] == 50, 'unknown checks must not count as 0'
    assert score_path({'a': 0, 'b': 0}, [{'target': 'x', 'fixes': ['a']}, {'target': 'y', 'fixes': ['b']}]) == [('x', 50), ('y', 100)], 'score path is wrong'
    assert score_path({'a': 0, 'b': None}, [{'target': 'x', 'fixes': [], 'helps': ['a', 'b']}]) == [('x', 50)], 'helps must count as partial'
    assert numbers('AED 1.2M, 40% in 2021') == {'1.2', '40', '2021'}, 'number parser is wrong'
    b = Balance()
    b.feed(text)
    assert not b.errors and not b.stack, f'unbalanced HTML: {b.errors} {b.stack}'


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    content = json.load(open(src, encoding='utf-8'))
    doc = render(content, os.path.dirname(os.path.abspath(src)))
    check(doc, content)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(doc)
    print('OK', out, f'{len(doc) // 1024} KB')
