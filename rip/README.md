# Rip Corpus — Hub

Curated, cleaned content ripped from websites, organized per source. Each
source folder holds its corpus and its summaries together.

## Structure

```
rip/
└── balanceanddizziness.org/   # source site: corpus + summaries in one folder
    ├── raw/                   # original HTML pages (curl)
    ├── clean/                 # extracted markdown article content
    ├── summaries/             # condensed cross-page summaries for this source
    │   ├── causes.md
    │   ├── treatments.md
    │   └── personal-experiences.md
    ├── sitemaps/              # sitemap XML + full URL list
    ├── extract.py             # extraction pipeline for this site
    └── README.md              # page inventory and pipeline docs
```

## Sources

| Source | Topic | Folder |
|---|---|---|
| [balanceanddizziness.org](https://balanceanddizziness.org) | PPPD and vestibular disorders | [balanceanddizziness.org/](balanceanddizziness.org/) |

## Adding a new source

1. `mkdir -p rip/<site-domain>/{raw,clean,summaries,sitemaps}`
2. Save HTML pages into `<site-domain>/raw/` (curl works well).
3. Copy and adapt an extractor script into `<site-domain>/extract.py`;
   run it to produce markdown in `<site-domain>/clean/`.
4. Write a page inventory at `<site-domain>/README.md`.
5. Write summaries under `<site-domain>/summaries/` and link them back to
   the corpus with relative paths (`../clean/...`).
6. Add a row to the Sources table above.

## Conventions

- Corpus files keep the site's own wording; summaries condense and cite
  back into the corpus by relative link.
- Summaries are written in plain, direct language — no filler, no
  significance inflation, facts sourced from the corpus.
- Everything commits to git as one corpus.
