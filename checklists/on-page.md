# On-Page SEO Checklist

Per-page checks for titles, meta descriptions, headings, images, content depth, and internal linking. The specific thresholds below match what `seo-playbook audit` and `seo-playbook meta` actually check in this repo (see `scripts/seo_audit.py` and `scripts/meta_generator.py`) — run `seo-playbook audit <url>` to check all of them at once.

## Title Tag

- [ ] Present on every page (missing `<title>` is a hard error)
- [ ] 30-60 characters — shorter reads as thin, longer gets truncated in search results
- [ ] Primary keyword included naturally, near the front
- [ ] Unique per page; no sitewide duplicate titles
- [ ] Brand suffix applied consistently (`seo-playbook meta --title "..." --brand "..."` generates this, dropping the brand automatically if it would push the title over length)

## Meta Description

- [ ] Present on every page
- [ ] 70-160 characters — under-length wastes snippet real estate, over-length gets truncated
- [ ] Written as a compelling, accurate summary, not keyword-stuffed
- [ ] Unique per page

## Headings

- [ ] Exactly one `<h1>` per page (zero or multiple are both flagged)
- [ ] Heading hierarchy is logical (no skipped levels, e.g. h2 straight to h4)
- [ ] Headings describe the content that follows, not generic labels

## Content

- [ ] At least ~300 words of substantive body content (below this, a page reads as thin)
- [ ] Content matches the search intent behind the target keyword
- [ ] Facts are specific and checkable, not vague filler
- [ ] Content reviewed for freshness on a recurring schedule, not written once and forgotten

## Images

- [ ] Every `<img>` has descriptive, non-generic `alt` text
- [ ] Images have explicit `width`/`height` attributes (prevents layout shift)
- [ ] Below-the-fold images use `loading="lazy"`
- [ ] Images compressed/served in a modern format (WebP/AVIF) where supported

## Links

- [ ] At least one relevant internal link per page (zero internal links is flagged)
- [ ] Internal links use descriptive anchor text, not "click here"
- [ ] Outbound links to authoritative sources where they support a claim
- [ ] No broken internal links — `seo-playbook check-links`

## Canonical & Indexability

- [ ] Self-referencing canonical tag present
- [ ] Page is not accidentally marked `noindex`
- [ ] URL is clean, lowercase, hyphenated, and stable

## Structured Data

- [ ] Appropriate schema type applied (`Article`, `Product`, `FAQPage`, etc. — `seo-playbook schema article|faq`)
- [ ] Schema validated against the live page — `seo-playbook schema validate page.html`

## References

- `scripts/seo_audit.py` — the on-page audit these checks are drawn from
- `scripts/meta_generator.py` — title/meta length constants and generation logic
- [SEO Book, Chapter 14: Structured Data & Schema Markup](../docs/books/complete/seo/chapter-14.md)
