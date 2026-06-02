# On-Device Intelligence — NeurIPS 2026 Workshop Website

> **Beyond the cloud, into the world.**

## Editing content

All editable content lives in the `content/` folder. Each file is a Markdown file with a YAML frontmatter block (between the `---` lines) and, for prose sections, a Markdown body below.

| File | What it controls |
|------|-----------------|
| `content/hero.md` | Title, subtitle, venue, date, CTA buttons |
| `content/about.md` | Workshop description (free Markdown prose) |
| `content/schedule.md` | Morning / afternoon schedule rows |
| `content/speakers.md` | Keynote speaker cards |
| `content/topics.md` | Research topic list |
| `content/submit.md` | Call for papers text + evaluation criteria |
| `content/dates.md` | Important deadline table |
| `content/organizers.md` | Organizer cards |
| `content/contact.md` | Contact information |

### Adding a confirmed speaker

Open `content/speakers.md` and replace a `tba: true` entry with:

```yaml
- name: "Jane Doe"
  affiliation: "MIT CSAIL"
  url: "https://janedoe.com"
  photo: "assets/speakers/jane_doe.jpg"   # optional — leave blank for initials
  bio: |
    Jane is a professor at MIT CSAIL specializing in efficient
    inference for large language models on edge devices.
```

Place speaker photos in `assets/speakers/` (JPG or PNG, ideally square, ≥ 200×200 px).

### Adding an organizer photo

In `content/organizers.md`, add a `photo:` field:

```yaml
- name: "Niao He"
  initials: "NH"
  role: "Associate Professor, CS · ETH Zurich"
  photo: "assets/organizers/niao_he.jpg"
```

## Building locally

```bash
pip install -r requirements.txt
python build.py
# → index.html is updated
```

Open `index.html` in a browser to preview.

## Deploying to GitHub Pages

### Automatic (recommended)

Push any change to `main` — the GitHub Actions workflow in `.github/workflows/build.yml` will run `build.py` automatically and deploy the result to GitHub Pages.

**One-time setup:**
1. Push this repo to GitHub.
2. Go to **Settings → Pages → Source** and set it to the `gh-pages` branch, root folder.
3. Done — every push to `main` rebuilds and deploys the site.

### Manual

```bash
python build.py
git add index.html
git commit -m "Rebuild site"
git push
```

If you prefer to serve from the `main` branch directly (no Actions), set Pages source to `main` / root.

## Folder structure

```
├── index.html              ← auto-generated (do not edit by hand)
├── build.py                ← build script
├── requirements.txt
├── README.md
├── content/
│   ├── hero.md
│   ├── about.md
│   ├── schedule.md
│   ├── speakers.md
│   ├── topics.md
│   ├── submit.md
│   ├── dates.md
│   ├── organizers.md
│   └── contact.md
├── assets/
│   ├── speakers/           ← speaker photos here
│   └── organizers/         ← organizer photos here
└── .github/
    └── workflows/
        └── build.yml
```
