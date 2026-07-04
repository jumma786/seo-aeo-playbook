# CLI Reference

The `seo-playbook` command wires every `scripts/` module up as a subcommand. Install the package (`pip install -e .`) to get the `seo-playbook` entry point, or run any command as `python -m cli.main <command>`.

```bash
seo-playbook --help
```

```text
Usage: seo-playbook [OPTIONS] COMMAND [ARGS]...

  seo-playbook: SEO, AEO, and GEO automation toolkit.

Options:
  --config FILE  Path to a seo-playbook.yml config file (defaults to ./seo-
                 playbook.yml if present).
  -v, --verbose  Enable debug logging.
  --help         Show this message and exit.
```

Run `seo-playbook init` in a project directory to create a `seo-playbook.yml` with `brand`/`domain`/`output_dir`/`default_similarity_threshold` defaults — several commands below (`robots`, `meta`, `cluster`, `keyword-map suggest`) read from it automatically.

## Schema & validation

### `schema article`

Generate an `Article` schema and print it as a `<script>` tag.

```text
Options:
  --headline TEXT        [required]
  --author TEXT          [required]
  --date-published TEXT  [required]
  --date-modified TEXT
  --output FILE          Write to a file instead of stdout.
```

### `schema faq JSON_FILE`

Generate a `FAQPage` schema from a JSON file of `[question, answer]` pairs. `--output FILE` writes to a file instead of stdout.

### `schema validate INPUT_FILE`

Validate JSON-LD markup in an HTML page (extracts every `<script type="application/ld+json">` block) or a standalone `.json` schema file. Exits non-zero if any error-severity issue is found — usable as a CI gate.

## Audits

### `audit URL`

Fetch a URL and run an on-page SEO audit (title/meta length, headings, images, canonical, robots meta, thin content, internal/external links). `--timeout FLOAT` (default `10.0`).

### `page-speed URL`

Fetch a URL and run a static page-speed audit: render-blocking scripts/stylesheets, images missing width/height (CLS risk), missing `loading="lazy"`, unoptimized Google Fonts, page weight, and measured time-to-first-byte. `--timeout FLOAT` (default `10.0`).

### `site-audit URLS_FILE`

Audit multiple pages (one URL per line) for SEO, schema, and performance issues in one pass — fetches each page once and runs `audit` + `schema validate` + `page-speed` against the same HTML. Exits non-zero if any page failed to fetch or has schema errors. `--timeout FLOAT` (default `10.0`).

### `check-links INPUT_FILE`

Check links for broken URLs and redirects. A `.html` file has its links extracted and checked; any other file is a plain text list of URLs, one per line. Exits non-zero if any broken link is found. `--base-url TEXT` (resolve relative links in HTML input), `--timeout FLOAT` (default `10.0`).

## Sitemaps, robots.txt, and llms.txt

### `sitemap URLS_FILE OUTPUT_FILE`

Generate an XML sitemap from a file of absolute URLs (one per line).

### `robots OUTPUT_FILE`

Generate a robots.txt file. `--disallow TEXT` (repeatable), `--sitemap-url TEXT` (repeatable — defaults to `https://<domain>/sitemap.xml` if `domain` is set in config and no `--sitemap-url` is given).

### `llms generate SPEC_FILE`

Generate an `llms.txt` file from a JSON spec (`name`, `summary`, `sections`), following the llmstxt.org convention. `--output FILE` writes to a file instead of stdout.

### `llms audit-crawlers ROBOTS_FILE`

Audit a robots.txt file for AI crawler (GPTBot, ClaudeBot, PerplexityBot, etc.) accessibility, flagging crawlers unintentionally blocked by a blanket rule.

## Keywords, entities, and internal linking

### `cluster KEYWORDS_FILE`

Cluster keywords (one per line) by lexical token-overlap similarity. `--threshold FLOAT` (0.0-1.0, defaults to config's `default_similarity_threshold`).

### `keyword-map audit MAPPINGS_FILE`

Audit an existing keyword-to-URL mapping (JSON list of `{keyword, url}`) for cannibalization — keywords assigned to more than one URL.

### `keyword-map suggest KEYWORDS_FILE PAGES_FILE`

Suggest a target URL for each keyword from a set of existing pages (JSON `{url: title}`), reusing `cluster`'s similarity scoring. `--threshold FLOAT` override.

### `entities CONTENT_FILE`

Extract entity mentions (Person/Organization/Date) with a frequency-based salience score. `--compare FILE` reports entities a competitor file mentions that `CONTENT_FILE` doesn't (content-gap analysis).

### `link-suggestions PAGES_FILE`

Suggest internal links and flag orphan pages from a JSON page list (`url`, `title`, `body`, `keywords`, `links_to`). `--max-per-page INTEGER` (default `5`).

### `geo-score CONTENT_FILE`

Score content passages for AI-citation readiness (self-contained subject naming, passage length, specific facts, structural labels). A `.html` file has its `<p>` tags scored; anything else is treated as Markdown/plain text split on blank lines.

## Content generation

### `meta`

Generate an SEO title tag and/or meta description. `--title TEXT`, `--brand TEXT` (defaults to config's `brand`), `--description TEXT`.

### `content-brief SPEC_FILE`

Generate a content brief (clustered H2 sections with word-count targets, title/meta guidance) from a JSON spec (`primary_keyword`, `related_keywords`, `target_word_count`, `questions`, `entities`). `--output FILE`.

### `faq FAQ_FILE`

Generate a Markdown FAQ section and matching `FAQPage` schema from a JSON file of `{question, answer}` objects, with citability validation (question phrasing, answer length, dangling-pronoun openers). `--output FILE`.

### `blog-scaffold SPEC_FILE`

Scaffold a new blog post — frontmatter, a section-by-section outline (as writer TODOs, not fabricated prose), an FAQ skeleton, and an `Article` schema — from a JSON spec combining blog metadata with a content-brief spec. `--output FILE`.

## Local SEO page generators

Both enforce quality gates (unique content per page, no boilerplate duplicated across sibling pages) before rendering; pass `--skip-quality-gates` to bypass (not recommended).

### `location-pages SPECS_FILE OUTPUT_DIR`

Generate governed pages for storefront/multi-location businesses (full NAP, hours, `LocalBusiness` schema) from a JSON spec list.

### `service-pages SPECS_FILE OUTPUT_DIR`

Generate governed pages for service-area businesses (no street address — schema uses `areaServed` instead, to avoid a false physical-presence claim) from a JSON spec list.

## Documentation tooling

### `generate-toc BOOK_DIRECTORY`

Generate a book's `| # | Chapter | Focus |` table of contents from its `chapter-*.md` files. `--output FILE`.

### `generate-readme SPEC_FILE`

Generate a full book README.md (title, description, table of contents, related books, license line) from a JSON spec. `--output FILE`.

## Project setup

### `init [DIRECTORY]`

Scaffold a new project's `seo-playbook.yml` config file. `--brand TEXT`, `--domain TEXT`, `--output-dir TEXT`, `--similarity-threshold FLOAT`, `--force` (overwrite an existing config).
