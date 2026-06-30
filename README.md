# Pankaj Kumar Chauhan — personal site (Jekyll edition)

A static academic site built with Jekyll. Same visual design as before;
the difference is this is now a real static-site-generator project that
deploys **free** on GitHub Pages, with content kept in two plain data
files instead of a single HTML file.

## What to edit

| To change...                                                   | Edit this file              |
|------------------------------------------------------------------|------------------------------|
| Name, title, hero text, About, links (ORCID/Scholar/etc.), research projects, software repos, presentations, honors, committee service, societies, licenses, "Beyond the research" | `_data/profile.yml` |
| **Publications** (add/remove/update a paper, citation counts)    | `_data/publications.bib` — standard BibTeX |
| Colors, fonts, section order, which sections appear at all, search/filter/BibTeX on or off, portrait photo vs. initials, footer year | `_data/settings.yml` |

You should not need to touch `index.html`, `_layouts/default.html`,
`assets/`, or `scripts/` for routine content OR appearance updates —
those are the template/tooling; the three data files are everything
you'd normally want to change.

## Publications: real BibTeX, not a custom format

`_data/publications.bib` is a normal `.bib` file — the same format every
reference manager and Google Scholar already export. You don't have to
write entries by hand:

- **Google Scholar**: go to your profile, check the boxes next to the
  papers you want, click **Export → BibTeX**, paste the result in.
- **Zotero / Mendeley / EndNote**: select your references → Export →
  BibTeX format.
- **PubMed**: select citations → Send to → Citation manager, which most
  reference managers can then export as BibTeX.

A small Python script (`scripts/bib_to_yaml.py`) converts that `.bib`
file into the YAML structure the page templates actually loop over
(`_data/publications.yml` — generated, gitignored, never hand-edited).
**GitHub Actions runs this automatically on every push** — you only ever
touch the `.bib` file.

One non-standard field the script understands, safe to include in a real
`.bib` file because reference managers just ignore fields they don't
recognize: `citations = {12}` — the current Google Scholar citation
count for that paper. This is the only thing you'll need to revisit
periodically; the Research Impact section (total citations, h-index,
i10-index, first-author count) recomputes itself from this field on
every build.

If you want to preview locally before pushing, run the conversion once
yourself first (see "Setting up Ruby/Jekyll the free way" below for the
full local-preview steps):

```bash
pip install -r requirements.txt
python3 scripts/bib_to_yaml.py
bundle exec jekyll serve
```

## Configuring appearance and structure (`_data/settings.yml`)

This file controls how the site looks and is laid out, independent of
the actual words in it:

- **`theme:`** — every color and font is a named value here (e.g.
  `color_accent`, `font_serif`). Change one, rebuild, done — no CSS
  knowledge needed. These get injected as CSS custom properties that
  override `assets/css/style.css`'s defaults.
- **`sections:`** — an ordered list. Reorder this list to reorder the
  page. Set `enabled: false` on any entry to remove it from both the
  nav menu and the page entirely — they're driven by the same list, so
  they can't drift out of sync. Rename `label`/`heading` here too.
- **`features:`** — independent on/off switches for the publication
  search box, the year/type filter dropdowns, the BibTeX export button,
  scroll-reveal animation, and nav scroll-spy highlighting.
- **`portrait:`** — switch between initials (default) and an actual
  photo (`mode: image`, then point `image_path` at your file).
- **`footer.year_mode`** — `auto` always shows the current year at
  build time; `manual` lets you pin a specific year.

## Adding your ORCID (or any link)

Open `_data/profile.yml`, find the `links:` list, and fill in the `url:`
for the `orcid` entry (currently blank — I couldn't independently verify
an ORCID for you, see note at the bottom). Any link with `url: ""` is
automatically hidden everywhere (Contact section, footer, About sidebar)
— there's nothing else to clean up.

## Setting up Ruby/Jekyll the free way (no local install needed)

You do **not** need to install Ruby or Jekyll on your own computer at all.
The included `.github/workflows/jekyll.yml` workflow builds the site on
GitHub's own free servers every time you push, then deploys it — your
machine never runs Ruby.

### One-time setup

1. Create a new repository on GitHub (public or private both work for
   Pages on a free personal account) and push this folder to it.
2. In the repo, go to **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **GitHub Actions**
   (not "Deploy from a branch" — that uses GitHub's restricted safe-mode
   Jekyll build, which can't run the workflow included here).
4. Push to `main`. Check the **Actions** tab — you'll see "Build and
   deploy Jekyll site to GitHub Pages" running. When it finishes (1–2
   minutes), your site is live at `https://yourusername.github.io/reponame`.
5. Open `_config.yml` and set `url:` to that address (and `baseurl:` to
   `/reponame` if it's not a `username.github.io` repo) so absolute links
   and the sitemap are correct.

After that, every future push to `main` rebuilds and redeploys
automatically — you edit `_data/profile.yml` or `_data/publications.yml`,
commit, push, and the live site updates itself within a minute or two.

### If you ever want to preview locally first

This needs Ruby + Bundler installed once:

```bash
gem install bundler
bundle install        # reads the Gemfile, installs the exact Jekyll
                       # version GitHub Pages uses — this is the key
                       # line that avoids the "wrong builder version"
                       # problem from before
bundle exec jekyll serve
```

Then open `http://localhost:4000`. This step is optional — pushing to
GitHub and watching the Actions tab works fine without it.

## Files

```
_data/profile.yml         ← your profile, links, projects, talks, honors, etc.
_data/publications.bib    ← your publications — standard BibTeX, the only file you edit
_data/publications.yml    ← GENERATED from the .bib file — gitignored, never hand-edited
_data/settings.yml        ← theme colors/fonts, section order/visibility, feature toggles, portrait mode, footer year
scripts/bib_to_yaml.py    ← the conversion script (runs automatically in CI)
requirements.txt          ← Python deps for that script (bibtexparser, PyYAML)
_config.yml               ← site title/description/plugins — set url/baseurl here
Gemfile                   ← pins Jekyll to the exact version GitHub Pages uses
.github/workflows/jekyll.yml  ← converts BibTeX, builds, and deploys on every push, free, on GitHub's servers
index.html                ← page template (Liquid) — loops over settings.yml's section list
_layouts/default.html     ← shared head/nav/footer wrapper, injects theme CSS vars and feature flags
_includes/sections/*.html ← one small template per section (about, research, publications, etc.)
assets/css/style.css      ← visual design (default token values — settings.yml overrides them)
assets/js/site.js         ← interactions only (search/filter, scroll-spy, BibTeX toggle), reads feature flags so it never errors on a feature you've turned off
cv.pdf                    ← add your real CV PDF here at the project root
portrait.jpg              ← add a real photo here, then set settings.yml's portrait.mode to "image"
```

## What happens as your publication list grows

Short answer: it keeps working, automatically, with no hardcoded limits.
Specifically:

- **Sorting, h-index/i10-index/citation totals** are computed from
  whatever is in `publications.bib` at build time — no count is
  hardcoded anywhere. Tested up to 114 synthetic entries with no
  slowdown (rendered in well under a tenth of a second).
- **Year and type filter dropdowns** are both generated from whatever
  years/types actually appear in your data — add a paper from a new year
  or a new kind of entry (a thesis, a preprint, a patent) and a working
  filter option appears for it automatically.
- **Author lists of any length** are handled the same way regardless of
  how many papers reference them — the truncation/bold-name logic
  already handles a 64-author paper correctly (see the Soeung et al.
  entry) and isn't position- or count-dependent.
- **New BibTeX entry types** beyond `@article`/`@inproceedings` (e.g.
  `@phdthesis`, `@misc` for preprints, `@book`) get mapped to sensible
  type labels automatically; you can always override with an explicit
  `type = {...}` field on any entry if the auto-detection guesses wrong
  (for example, an arXiv preprint exported as `@article` would otherwise
  be labeled "journal" — add `type = {preprint}` to that entry to fix it).
- **Duplicate citation keys or missing titles/authors/years** — if you
  bulk-paste a Scholar export and accidentally end up with two entries
  sharing a key, or one missing a field, the build won't crash or
  silently corrupt the page. The conversion script keeps the first
  occurrence of a duplicate and prints a warning in the GitHub Actions
  log telling you exactly which key to rename.

The one thing that doesn't auto-scale is presentation: past a few hundred
entries, a single long scrolling list (even with search/filter) gets
unwieldy. If you ever get there, pagination or year-grouping would be a
reasonable next addition — not needed for a CV-sized publication list,
but worth knowing the ceiling.

## Honest notes on testing

I don't have network access to rubygems.org in my own environment, so I
could not run the actual `bundle exec jekyll build` here. What I did
instead, to catch errors before you push:

- Validated all three YAML data files parse correctly.
- **Stress-tested growth directly**, since that's a real question: generated
  a synthetic 115-entry `.bib` file (going from your 13 real entries to
  114 after dedup) with randomized years/citations/author counts, a
  deliberate duplicate citation key, a missing-title entry, and new entry
  types (`@phdthesis`, `@misc`) not in the original file. Running the real
  script against it surfaced two genuine gaps, both now fixed: the type
  filter dropdown was hardcoded to only "Journal"/"Conference" (now
  generated dynamically from whatever types actually exist, like the year
  dropdown already was), and the script had no handling for duplicate
  keys or missing required fields (now warns and skips/continues instead
  of producing a broken or duplicated entry). Re-ran after fixing: 114
  entries converted correctly, the duplicate was caught and skipped, the
  missing title was flagged as a warning without failing the build, new
  types ("preprint", "thesis") appeared correctly in the filter dropdown,
  the page rendered in 43ms, and the computed metrics (3,899 citations,
  h-index 42, i10-index 94) matched an independent calculation exactly.
- **Ran the actual `scripts/bib_to_yaml.py` script against the real
  `publications.bib`** (this one I could fully execute — it only needs
  `bibtexparser`/`PyYAML` from PyPI, which I do have access to, unlike
  RubyGems). It surfaced and I fixed two real bugs: author initials that
  were already abbreviated in the source (e.g. "PK") were being
  re-abbreviated down to a single letter ("P"), and BibTeX's brace
  protection on compound surnames (`{Hernandez Gonzalez}`) was leaking
  literal braces into the displayed name. Re-ran after each fix and
  confirmed all 13 entries convert correctly, including verifying
  Chauhan's name and the compound surname both render right.
- Rendered the Liquid templates with a Python Liquid engine (close to,
  but not identical to, Ruby's — notably its standard `include` tag
  binds passed parameters as bare variables, while Jekyll's binds them
  under `include.varname`; I accounted for this difference rather than
  letting it block testing, using throwaway test copies to validate
  logic while shipping the real, Jekyll-correct files unchanged).
- Working through that, fixed three real bugs: a filter used inside an
  `{% if %}` tag (not allowed in Liquid), a sort crashing because some
  publications had a `citations` field and others didn't, and an
  unquoted `{% include sections/about.html %}` path that some Liquid
  parsers reject (now quoted, which both Jekyll and standard Liquid
  accept unambiguously).
- Cross-checked the computed Research Impact numbers (142 citations,
  h-index 6, i10-index 5, 4 first-author papers) against an independent
  plain-Python calculation — they matched.
- Specifically tested that editing `settings.yml` alone — reordering
  sections, disabling one entirely, changing a theme color, turning off
  search/BibTeX — actually changes the rendered output, since that's
  the whole point of this layer.
- Rendered the full page output in a browser and visually compared every
  section against the original design pixel-for-pixel.

This gives reasonable confidence, but it is not the same as a real Jekyll
build. The very first GitHub Actions run after you push is the actual
test — check the Actions tab; if it fails, send me the error and I'll fix
it directly.

## On your ORCID

I searched but couldn't find a verified ORCID for you — it isn't listed in
your CV's social-media links either, and the LinkedIn search results that
came up for "Pankaj Kumar Chauhan" + ORCID were clearly a mix of other
people with the same name (a CUNY/Hunter College PhD student, a software
engineer, etc.), so I didn't want to guess and attribute someone else's ID
to you. The field is wired up and ready — just paste yours into
`_data/profile.yml` if you have one.
