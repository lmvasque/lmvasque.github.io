# lmvasque.github.io

Laura Vásquez-Rodríguez's personal academic website: <https://lmvasque.github.io/>

A Jekyll site, originally from the [academicpages](https://github.com/academicpages/academicpages.github.io)
template, trimmed down to the parts this site actually uses. Pushing to `master`
deploys it through GitHub Pages.

## Running it locally

The local Ruby is usually too old or too new for Jekyll 3.9, so Docker is the
path of least resistance:

```bash
docker compose up --build     # first run; afterwards just: docker compose up
```

Then open <http://localhost:4000>.

`_config.yml` is **not** reloaded while the server runs. After editing it,
restart the container, or you will spend a while wondering why nothing changed.
Inline CSS and JavaScript are embedded in cached pages, so hard-refresh the
browser after changing those.

Native alternative, if you'd rather not use Docker:

```bash
brew install ruby@3.3         # the version GitHub Pages runs
export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH"
bundle install
bundle exec jekyll serve -l -H localhost
```

## Adding content

Content is one markdown file per item, named `YYYY-MM-DD-slug.md`. The date
prefix matters: it sets the permalink and the ordering.

| What | Where |
|---|---|
| Publications | `_publications/` |
| Talks | `_talks/` |
| Awards | `_data/awards.yml` (one list entry each) |
| Experience, education | `_data/cv.yml` |
| Pages | `_pages/` |
| Slides, posters, PDFs | `files/`, served from `/files/…` |

Front matter drives everything. Publications take `paperurl`, `slidesurl`,
`posterurl`, `videourl` and `codeurl`; each one present adds a button. Talks take
`talkurl`, `slidesurl` and `videourl`. `authors` is a comma-separated string, and
your own name is bolded automatically.

After adding or renaming any of those, check the links:

```bash
python3 scripts/validate_urls.py               # every link: status + content type
python3 scripts/validate_urls.py --local-only  # just files/, no network
```
