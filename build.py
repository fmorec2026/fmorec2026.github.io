#!/usr/bin/env python3
"""
build.py — compile content/*.md files into index.html
Usage:  python build.py
Needs:  pip install pyyaml markdown
"""

import os, re, html, yaml, markdown as md_lib

CONTENT = "content"
OUT     = "index.html"

# ── helpers ──────────────────────────────────────────────────────────────────

def parse(filename):
    """Return (frontmatter_dict, rendered_html_body) from a content/*.md file."""
    path = os.path.join(CONTENT, filename)
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    fm, body = {}, ""
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm   = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
    else:
        body = raw.strip()
    body_html = md_lib.markdown(body, extensions=["nl2br", "tables"]) if body else ""
    return fm, body_html

def e(text):
    """HTML-escape a string (for values coming from YAML)."""
    return html.escape(str(text)) if text else ""

def initials_from_name(name):
    parts = name.strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()

# ── section renderers ─────────────────────────────────────────────────────────

def render_hero(fm, _body):
    return f"""
<div id="hero">
  <div class="hero-inner">
    <div class="hero-tag">{e(fm.get('badge',''))}</div>
    <h1>{e(fm.get('title',''))}<br><em>{e(fm.get('title_em',''))}</em></h1>
    <p class="hero-sub">{e(fm.get('subtitle',''))}</p>
    <div class="hero-meta">
      <span><strong>{e(fm.get('date',''))}</strong></span>
      <span class="hero-meta-sep">·</span>
      <span>{e(fm.get('venue',''))} <span style="color:var(--light);font-size:13px;">{e(fm.get('venue_note',''))}</span></span>
      <span class="hero-meta-sep">·</span>
      <span>{e(fm.get('attendees',''))}</span>
    </div>
    <div class="hero-links">
      <a href="{e(fm.get('cta_primary_url','#'))}" class="btn btn-primary" target="_blank" rel="noopener">{e(fm.get('cta_primary_text','Submit'))}</a>
      <a href="{e(fm.get('cta_secondary_url','#about'))}" class="btn btn-outline">{e(fm.get('cta_secondary_text','Learn More'))}</a>
    </div>
  </div>
</div>"""

def render_about(fm, body):
    return f"""
<section id="about">
  <div class="section-inner">
    <h2>{e(fm.get('title','About'))}</h2>
    {body}
  </div>
</section>"""

def render_schedule(fm, _body):
    def rows(items):
        out = []
        for item in (items or []):
            typ  = item.get('type', '')
            cls  = f"sched-label {typ}" if typ else "sched-label"
            out.append(f'<div class="sched-row"><span class="sched-time">{e(item.get("time",""))}</span>'
                       f'<span class="{cls}">{e(item.get("label",""))}</span></div>')
        return "\n".join(out)

    schedule_html  = rows([*(fm.get('morning', []) or []), *(fm.get('afternoon', []) or [])])
    description    = fm.get('description', '')
    note           = fm.get('note', '')

    return f"""
<section id="schedule">
  <div class="section-inner">
    <h2>{e(fm.get('title','Schedule'))}</h2>
    {'<p class="section-lead">' + e(description) + '</p>' if description else ''}
    <div class="schedule-list">{schedule_html}</div>
    {'<p style="margin-top:1.5rem;font-size:13.5px;color:var(--light);">' + e(note) + '</p>' if note else ''}
  </div>
</section>"""

def render_speakers(fm, _body):
    cards = []
    for s in (fm.get('speakers') or []):
        if s.get('tba'):
            cards.append(
                '<div class="speaker-card">'
                '<div class="speaker-photo"><span style="color:var(--light);font-style:normal;font-size:1.1rem;">TBA</span></div>'
                '<div class="speaker-name" style="color:var(--light);font-weight:400;font-style:italic;">To be announced</div>'
                '</div>')
        else:
            name  = e(s.get('name',''))
            affil = e(s.get('affiliation',''))
            url   = s.get('url','')
            photo = s.get('photo','')
            bio   = e(s.get('bio',''))

            if photo:
                photo_html = f'<img src="{e(photo)}" alt="{name}" loading="lazy">'
            else:
                inits = e(initials_from_name(s.get('name','')))
                photo_html = f'<span>{inits}</span>'

            name_html = f'<a href="{e(url)}" style="color:inherit;text-decoration:none;">{name}</a>' if url else name

            bio_html = (
                f'<button class="bio-toggle" aria-expanded="false" onclick="toggleBio(this)">Read bio</button>'
                f'<div class="bio-panel" hidden><p class="speaker-bio">{bio}</p></div>'
            ) if bio else ''
            cards.append(
                f'<div class="speaker-card">'
                f'<div class="speaker-photo">{photo_html}</div>'
                f'<div class="speaker-name">{name_html}</div>'
                f'<div class="speaker-affil">{affil}</div>'
                f'{bio_html}'
                f'</div>')

    grid = "\n".join(cards)
    return f"""
<section id="speakers">
  <div class="section-inner">
    <h2>{e(fm.get('title','Keynote Speakers'))}</h2>
    <div class="speakers-grid">{grid}</div>
  </div>
</section>"""

def render_topics(fm, _body):
    items = []
    for i, t in enumerate(fm.get('topics') or [], 1):
        num  = str(i).zfill(2)
        items.append(
            f'<li><span class="topic-num">{num}</span>'
            f'<div class="topic-body"><h4>{e(t.get("title",""))}</h4>'
            f'<p>{e(t.get("description",""))}</p></div></li>')

    intro = f'<p>{e(fm.get("intro",""))}</p>' if fm.get("intro") else ""
    return f"""
<section id="topics">
  <div class="section-inner">
    <h2>{e(fm.get('title','Topics'))}</h2>
    {intro}
    <ul class="topics-list">{"".join(items)}</ul>
  </div>
</section>"""

def render_submit(fm, body):
    criteria_items = "".join(f"<li>{e(c)}</li>" for c in (fm.get('criteria') or []))
    submit_url    = e(fm.get('openreview_url', 'https://openreview.net'))
    submit_label  = e(fm.get('openreview_label', 'Submit on OpenReview'))
    note          = e(fm.get('conflict_note', ''))

    return f"""
<section id="submit">
  <div class="section-inner">
    <h2>{e(fm.get('title','Call for Papers'))}</h2>
    {body}
    <div class="cfp-box">
      <h3>Evaluation Criteria</h3>
      <ul>{criteria_items}</ul>
      <a href="{submit_url}" class="btn btn-primary" target="_blank" rel="noopener">{submit_label}</a>
      {'<p class="cfp-note">' + note + '</p>' if note else ''}
    </div>
  </div>
</section>"""

def render_dates(fm, _body):
    rows = []
    for d in (fm.get('dates') or []):
        hl  = ' class="hl"' if d.get('highlight') else ''
        rows.append(f'<tr{hl}><td>{e(d.get("label",""))}</td><td>{e(d.get("date",""))}</td></tr>')

    note = f'<p style="font-size:13.5px;color:var(--light);">{e(fm.get("note",""))}</p>' if fm.get("note") else ""
    return f"""
<section id="dates">
  <div class="section-inner">
    <h2>{e(fm.get('title','Important Dates'))}</h2>
    {note}
    <table class="dates-table">{"".join(rows)}</table>
  </div>
</section>"""

def render_organizers(fm, _body):
    cards = []
    for o in (fm.get('organizers') or []):
        name   = e(o.get('name',''))
        role   = e(o.get('role',''))
        url    = o.get('url','')
        photo  = o.get('photo','')
        inits  = e(o.get('initials') or initials_from_name(o.get('name','')))

        if photo:
            photo_html = f'<img src="{e(photo)}" alt="{name}" loading="lazy">'
        else:
            photo_html = f'<span>{inits}</span>'

        name_html = f'<a href="{e(url)}" style="color:inherit;text-decoration:none;">{name}</a>' if url else name

        cards.append(
            f'<div class="speaker-card">'
            f'<div class="speaker-photo">{photo_html}</div>'
            f'<div class="speaker-name">{name_html}</div>'
            f'<div class="speaker-affil">{role}</div>'
            f'</div>')

    note = fm.get('note','')
    return f"""
<section id="organizers">
  <div class="section-inner">
    <h2>{e(fm.get('title','Organizers'))}</h2>
    <div class="speakers-grid">{"".join(cards)}</div>
    {'<p style="margin-top:1.5rem;font-size:13.5px;color:var(--light);">' + e(note) + '</p>' if note else ''}
  </div>
</section>"""

def render_contact(fm, body):
    contacts_html = ""
    for c in (fm.get('contacts') or []):
        name  = e(c.get('name',''))
        email = e(c.get('email',''))
        contacts_html += f'{name} — <a href="mailto:{email}">{email}</a><br>\n'

    return f"""
<section id="contact">
  <div class="section-inner">
    <h2>{e(fm.get('title','Contact'))}</h2>
    {body}
    {'<p>' + contacts_html + '</p>' if contacts_html else ''}
  </div>
</section>"""

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
:root {
  --text: #1a1a1a; --muted: #555; --light: #888;
  --bg: #ffffff; --bg2: #f7f7f5;
  --accent: #1a6b5a; --accent-light: #e8f4f1;
  --border: #e0e0da; --link: #1a6b5a; --max: 860px;
}
body {
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
  font-size: 16px; line-height: 1.75;
  color: var(--text); background: var(--bg);
  -webkit-font-smoothing: antialiased;
}
nav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(255,255,255,0.96); backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border); padding: 0 1.5rem;
}
.nav-inner {
  max-width: var(--max); margin: 0 auto;
  display: flex; align-items: center; height: 52px;
  overflow-x: auto; -ms-overflow-style: none; scrollbar-width: none;
}
.nav-inner::-webkit-scrollbar { display: none; }
nav a {
  font-size: 13.5px; font-weight: 500; color: var(--muted);
  text-decoration: none; white-space: nowrap; padding: 0 1rem;
  height: 52px; display: flex; align-items: center;
  border-bottom: 2px solid transparent;
  transition: color .15s, border-color .15s;
}
nav a:first-child { padding-left: 0; }
nav a:hover { color: var(--accent); }
nav a.active { color: var(--accent); border-bottom-color: var(--accent); }
#hero {
  background: var(--bg2); background-size: cover; background-position: 58% 80%; background-repeat: no-repeat; border-bottom: 1px solid var(--border);
  padding: 5rem 1.5rem 4rem; text-align: center;
}
.hero-inner { max-width: var(--max); margin: 0 auto; }
.hero-tag {
  display: inline-block; background: var(--accent-light); color: var(--accent);
  font-size: 12px; font-weight: 600; letter-spacing: .1em;
  text-transform: uppercase; padding: .3rem .85rem; border-radius: 100px; margin-bottom: 1.5rem;
}
#hero h1 {
  font-family: 'IBM Plex Serif', serif; font-size: clamp(1.9rem,4.5vw,3rem);
  font-weight: 600; line-height: 1.2; margin-bottom: .5rem;
}
#hero h1 em { font-style: italic; color: var(--accent); }
.hero-sub { font-size: 1.22rem; font-weight: 600; color: var(--muted); margin-top: 1rem; max-width: 640px; margin-left: auto; margin-right: auto; }
.hero-meta { display: flex; flex-wrap: wrap; justify-content: center; gap: .4rem 1.4rem; margin-top: 2rem; font-size: 15px; color: var(--muted); }
.hero-meta strong { color: var(--text); font-weight: 500; }
.hero-meta-sep { color: var(--border); }
.hero-links { margin-top: 2rem; display: flex; gap: .75rem; justify-content: center; flex-wrap: wrap; }
.btn {
  display: inline-flex; align-items: center; gap: .4rem;
  font-size: 14px; font-weight: 500; padding: .6rem 1.4rem;
  border-radius: 5px; text-decoration: none;
  transition: all .15s; cursor: pointer;
  font-family: 'IBM Plex Sans', sans-serif; border: 1.5px solid transparent;
}
.btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.btn-primary:hover { background: #155248; border-color: #155248; }
.btn-outline { background: transparent; color: var(--accent); border-color: var(--accent); }
.btn-outline:hover { background: var(--accent-light); }
section { padding: 4.5rem 1.5rem; border-bottom: 1px solid var(--border); }
section:last-of-type { border-bottom: none; }
.section-inner { max-width: var(--max); margin: 0 auto; }
section h2 {
  font-family: 'IBM Plex Serif', serif; font-size: 1.7rem;
  font-weight: 600; color: var(--text); margin-bottom: 1.5rem;
}
section p { color: var(--muted); margin-bottom: 1rem; }
.section-lead { max-width: 720px; font-size: 15px; line-height: 1.65; }
section p:last-child { margin-bottom: 0; }
section ul, section ol { color: var(--muted); padding-left: 1.4rem; margin-bottom: 1rem; }
section li { margin-bottom: .3rem; }
section strong { color: var(--text); }
section em { font-style: italic; }
section a { color: var(--link); }
#about, #speakers, #submit, #organizers, #contact { background: var(--bg); }
#schedule, #topics, #dates { background: var(--bg2); }
.schedule-list { max-width: 720px; margin-top: .5rem; }
.schedule-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; margin-top: .5rem; }
.schedule-half h3 {
  font-size: 11.5px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase;
  color: var(--accent); margin-bottom: .9rem; padding-bottom: .5rem; border-bottom: 1px solid var(--border);
}
.sched-row { display: flex; gap: 1rem; align-items: flex-start; padding: .6rem 0; border-bottom: 1px solid #f0f0ec; font-size: 14px; }
.sched-row:last-child { border-bottom: none; }
.sched-time { min-width: 110px; color: var(--light); font-size: 12.5px; flex-shrink: 0; padding-top: 2px; }
.sched-label { color: var(--text); }
.sched-label.highlight { color: var(--accent); font-weight: 500; }
.sched-label.soft { color: var(--muted); font-style: italic; }
.sched-label.gold { color: #8a6000; font-weight: 500; }
.speakers-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(200px,1fr)); gap: 2rem; margin-top: .5rem; }
.speaker-card { text-align: center; }
.speaker-photo {
  width: 108px; height: 108px; border-radius: 50%;
  background: var(--bg2); border: 2px solid var(--border);
  margin: 0 auto .85rem; display: flex; align-items: center; justify-content: center;
  font-family: 'IBM Plex Serif', serif; font-size: 1.5rem; font-style: italic; color: var(--accent); overflow: hidden;
}
.speaker-photo img { width: 100%; height: 100%; object-fit: cover; }
.speaker-name { font-weight: 600; font-size: 15px; margin-bottom: .25rem; }
.speaker-affil { font-size: 13px; color: var(--muted); line-height: 1.4; }
.speaker-bio { font-size: 13px; color: var(--muted); margin-top: .5rem; text-align: left; }
.topics-list { list-style: none; margin-top: .5rem; }
.topics-list > li { padding: 1.1rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 1.2rem; align-items: flex-start; }
.topics-list > li:last-child { border-bottom: none; }
.topic-num { font-size: 11px; font-weight: 600; letter-spacing: .08em; color: var(--accent); background: var(--accent-light); border-radius: 100px; padding: .2rem .65rem; flex-shrink: 0; margin-top: 3px; }
.topic-body h4 { font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: .25rem; }
.topic-body p { font-size: 14px; color: var(--muted); margin: 0; }
.cfp-box { border: 1px solid var(--border); border-radius: 8px; background: var(--bg2); padding: 2rem; margin-top: 1.5rem; }
.cfp-box h3 { font-family: 'IBM Plex Serif', serif; font-size: 1.15rem; font-weight: 600; margin-bottom: .8rem; color: var(--text); }
.cfp-box ul { padding-left: 1.3rem; color: var(--muted); font-size: 14.5px; margin-bottom: 1.5rem; }
.cfp-box ul li + li { margin-top: .3rem; }
.cfp-note { margin-top: 1rem; font-size: 13px; color: var(--light); }
table.dates-table { width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 14.5px; }
table.dates-table tr { border-bottom: 1px solid var(--border); }
table.dates-table tr:last-child { border-bottom: none; }
table.dates-table td { padding: .9rem .4rem; vertical-align: top; }
table.dates-table td:first-child { width: 58%; }
table.dates-table td:last-child { font-size: 13.5px; color: var(--accent); text-align: right; white-space: nowrap; }
table.dates-table tr.hl { background: #fffbec; }
table.dates-table tr.hl td:first-child { font-weight: 600; color: #6b4800; }
table.dates-table tr.hl td:last-child { color: #6b4800; font-weight: 600; }
.org-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(240px,1fr)); gap: 1.2rem; margin-top: .5rem; }
.org-card { display: flex; align-items: center; gap: 1rem; padding: 1.1rem; border: 1px solid var(--border); border-radius: 8px; background: var(--bg2); }
.org-avatar { width: 50px; height: 50px; border-radius: 50%; background: var(--accent-light); border: 1.5px solid #c6e8e0; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; color: var(--accent); flex-shrink: 0; }
.org-name { font-size: 14px; font-weight: 600; margin-bottom: .15rem; }
.org-role { font-size: 12px; color: var(--muted); line-height: 1.45; }
footer { background: #1a1a1a; color: #999; padding: 2.5rem 1.5rem; text-align: center; font-size: 13.5px; }
.footer-inner { max-width: var(--max); margin: 0 auto; }
footer em { display: block; font-style: italic; color: #666; margin-top: .4rem; font-size: 13px; }
footer a { color: #aaa; text-decoration: none; }
footer a:hover { color: #fff; }

.bio-toggle {
  display: inline-block;
  margin-top: .6rem;
  font-size: 12px;
  font-weight: 500;
  color: var(--accent);
  background: none;
  border: 1px solid var(--accent);
  border-radius: 100px;
  padding: .2rem .75rem;
  cursor: pointer;
  font-family: 'IBM Plex Sans', sans-serif;
  transition: background .15s, color .15s;
}
.bio-toggle:hover { background: var(--accent-light); }
.bio-toggle.open { background: var(--accent); color: #fff; }
.bio-panel {
  margin-top: .75rem;
  text-align: left;
  overflow: hidden;
  max-height: 0;
  transition: max-height .35s ease, opacity .3s ease;
  opacity: 0;
}
.bio-panel.visible {
  max-height: 300px;
  opacity: 1;
}
.speaker-bio {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.6;
  margin: 0;
  padding: .75rem;
  background: var(--bg2);
  border-radius: 6px;
  border-left: 2px solid var(--accent);
}
@media (max-width: 640px) {
  #hero { background-position: 44% 92%; }
  .schedule-cols { grid-template-columns: 1fr; }
  .sched-time { min-width: 84px; font-size: 11.5px; }
  .org-grid { grid-template-columns: 1fr; }
  .speakers-grid { grid-template-columns: repeat(2,1fr); }
}
"""

JS = """
(function(){
  const sections = Array.from(document.querySelectorAll('section[id]'));
  const links    = document.querySelectorAll('nav a');
  function update(){
    let cur = '';
    sections.forEach(s => { if(window.scrollY >= s.offsetTop - 80) cur = s.id; });
    links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + cur));
  }
  window.addEventListener('scroll', update, {passive:true});
  update();
})();
"""

# ── assemble ──────────────────────────────────────────────────────────────────

def build():
    sections = [
        ("hero.md",        render_hero),
        ("about.md",       render_about),
        ("topics.md",      render_topics),
        ("speakers.md",    render_speakers),
        ("schedule.md",    render_schedule),
        ("submit.md",      render_submit),
        ("dates.md",       render_dates),
        ("organizers.md",  render_organizers),
        ("contact.md",     render_contact),
    ]

    hero_fm, _ = parse("hero.md")
    page_title = f"{hero_fm.get('title','')} {hero_fm.get('title_em','')} · NeurIPS 2026 Workshop"
    tagline    = e(hero_fm.get('tagline', ''))

    nav_links = '\n    '.join([
        '<a href="#about">About</a>',
        '<a href="#topics">Topics</a>',
        '<a href="#speakers">Keynote Speakers</a>',
        '<a href="#schedule">Schedule</a>',
        '<a href="#submit">Call for Papers</a>',
        '<a href="#dates">Important Dates</a>',
        '<a href="#organizers">Organizers</a>',
        '<a href="#contact">Contact</a>',
    ])

    body_parts = []
    for filename, renderer in sections:
        fm, body = parse(filename)
        body_parts.append(renderer(fm, body))

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(page_title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<nav>
  <div class="nav-inner">
    {nav_links}
  </div>
</nav>

{"".join(body_parts)}

<footer>
  <div class="footer-inner">
    <div>NeurIPS 2026 Workshop &mdash; On-Device Intelligence: Foundation Models under Real-World Constraints</div>
    <em>{tagline}</em>
    <div style="margin-top:1rem;font-size:12px;color:#555;">
      Organized by <a href="https://ethz.ch" target="_blank" rel="noopener">ETH Zurich</a>
      &amp; <a href="https://www.is.mpg.de" target="_blank" rel="noopener">MPI for Intelligent Systems</a>
    </div>
  </div>
</footer>

<script>{JS}</script>
</body>
</html>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"✓ Built {OUT} from {len(sections)} content files.")

if __name__ == "__main__":
    build()
