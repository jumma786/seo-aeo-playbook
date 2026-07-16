# Chapter 5: Indexing

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What is Indexing?
3. How Search Engines Index Pages
4. Index vs Crawl
5. HTML Processing
6. Canonical URLs
7. Duplicate Content
8. Noindex Directive
9. Robots.txt and Indexing
10. XML Sitemaps
11. JavaScript Indexing
12. Structured Data
13. Freshness Signals
14. Content Quality
15. Helpful Content
16. E-E-A-T
17. Index Coverage Report
18. Soft 404 Errors
19. Crawl Budget and Indexing
20. URL Parameters
21. Common Indexing Issues
22. Best Practices
23. Checklist
24. Summary
25. References

---

# 1. Introduction

Indexing is the process of storing and organizing web pages after they have been crawled. Search engines analyze a page's content, metadata, links, and structure before deciding whether it should be included in the search index.

Only indexed pages are eligible to appear in search results.

---

# 2. What is Indexing?

Once a page is crawled and rendered, a search engine parses its content, extracts signals (text, structured data, links, metadata), and decides whether to add it to the index — its searchable database of pages. A page can be crawled successfully and still never be indexed, if it's judged duplicate, thin, or otherwise low-value.

Factors that influence indexing include:

- Content quality
- Duplicate content
- Canonical tags
- Noindex directives
- Internal linking
- Structured data
- Website authority
- Technical health

---

# 3. How Search Engines Index Pages

Indexing involves parsing the rendered page into its constituent signals — visible text, headings, structured data, outbound and inbound links, and metadata — then storing a processed representation (not a literal copy) optimized for fast retrieval at query time. Modern indexing systems also generate semantic representations (embeddings) of content, not just keyword-based ones — see the [GEO Book, Chapter 5](../geo/chapter-05.md) for how this works mechanically.

---

# 4. Index vs Crawl

Crawling and indexing are distinct stages, and confusing them is a common source of misdiagnosis:

| | Crawl | Index |
|---|---|---|
| Question answered | Can the bot fetch this URL? | Should this URL be stored and made searchable? |
| Controlled by | `robots.txt`, server availability | `noindex`, content quality, duplication |
| A page can be... | Crawled but not indexed | Indexed without being *re*-crawled recently (using a cached version) |

A URL can be "Crawled - currently not indexed" in Search Console — successfully fetched, but deliberately excluded, usually for quality or duplication reasons.

---

# 5. HTML Processing

During indexing, a search engine parses the DOM to extract the primary content, distinguishing it from boilerplate (navigation, footers, ads) using layout and semantic HTML cues. Clean, semantic HTML (proper heading hierarchy, `<main>`/`<article>` where appropriate) helps this extraction; a page built entirely from generic `<div>` soup makes it harder for a search engine to identify what the page is actually about.

---

# 6. Canonical URLs

When multiple URLs serve duplicate or near-duplicate content, the canonical tag declares which one should represent the group in the index — consolidating ranking signals rather than splitting them across variants. Search engines treat the canonical tag as a strong hint, not an absolute directive, and can choose a different URL as canonical if other signals (like internal linking patterns) strongly disagree.

---

# 7. Duplicate Content

Duplicate content — identical or near-identical text across multiple URLs, whether on the same site or across sites — forces a search engine to choose one representative version, diluting signals across the rest. Common causes: URL parameters (session IDs, sort orders), `http`/`https` and `www`/non-`www` variants, printer-friendly page versions, and syndicated content republished without proper canonical attribution.

---

# 8. Noindex Directive

The `noindex` directive (via `<meta name="robots" content="noindex">` or an `X-Robots-Tag` HTTP header) tells a search engine not to include a page in the index, while still allowing it to be crawled — the reliable way to deliberately exclude a page, as opposed to `Disallow` in robots.txt, which can leave a page indexed with no visible content if it's still linked to externally.

---

# 9. Robots.txt and Indexing

Blocking a URL via `robots.txt` prevents crawling, but doesn't guarantee exclusion from the index — if other pages link to a disallowed URL, a search engine can still index the URL itself (typically with no title or snippet, just the bare URL), since it never crawled the page to see a `noindex` tag. For guaranteed exclusion, use `noindex` and allow crawling.

---

# 10. XML Sitemaps

A sitemap doesn't force indexing — it only aids discovery. Search Console's Index Coverage report will show sitemap URLs that were discovered but excluded, along with the stated reason (duplicate, noindexed, quality issues), making sitemaps a useful indexing *diagnostic* tool as well as a discovery aid.

---

# 11. JavaScript Indexing

Content added to the DOM via JavaScript can be indexed, but only after Google's separate rendering pass completes ([Chapter 4, Section 11](chapter-04.md)) — meaning JavaScript-dependent content is indexed later, and less reliably, than content present in the initial HTML. Many non-Google crawlers index JavaScript-rendered content far less consistently or not at all.

---

# 12. Structured Data

Structured data (JSON-LD) doesn't directly cause indexing, but it reinforces what a page is about and can unlock indexing-adjacent features like rich results and Knowledge Panel eligibility. Schema that contradicts a page's actual visible content is a documented Google guidelines violation and can undermine trust in the page's other signals. See [Chapter 14](chapter-14.md).

---

# 13. Freshness Signals

For queries with a genuine time-sensitivity (news, current events, "best X in 2026"), a search engine weighs how recently a page was published or meaningfully updated. Artificially bumping a "last updated" date without real content changes is both easy to detect and a Helpful Content risk, not a genuine freshness signal.

---

# 14. Content Quality

Thin, unoriginal, or low-substance content is a common reason a crawled page never gets indexed — search engines increasingly filter at index time based on whether a page provides genuine, non-duplicative value, not just whether it's technically crawlable. See [Chapter 9](chapter-09.md) for content quality standards in depth.

---

# 15. Helpful Content

Google's Helpful Content System evaluates whether content was created primarily to satisfy a genuine reader need versus primarily to attract search traffic (mass-produced, formulaic, or thin AI-generated content with no real added value). Sites where low-value content dominates can see sitewide indexing and ranking impact, not just on the affected pages themselves.

---

# 16. E-E-A-T

Experience, Expertise, Authoritativeness, and Trustworthiness signals feed into how a search engine judges content quality at index and ranking time, particularly for topics that can affect a reader's health, finances, or safety (YMYL). See [Chapter 12](chapter-12.md) for the full framework.

---

# 17. Index Coverage Report

Search Console's Index Coverage (Page Indexing) report categorizes every known URL as indexed, or excluded with a specific reason — `Duplicate without user-selected canonical`, `Crawled - currently not indexed`, `Blocked by robots.txt`, `Noindex`, and others. This report is the single most direct source of truth for diagnosing why a specific page isn't appearing in search.

---

# 18. Soft 404 Errors

A soft 404 is a page that displays "not found" or empty/thin content to users but returns an HTTP 200 status instead of a proper 404 — confusing search engines about whether the page genuinely exists. Ensure genuinely missing content returns a real 404 (or 410 for permanently removed content) rather than a 200-status placeholder page.

---

# 19. Crawl Budget and Indexing

Wasted crawl budget on low-value URLs (parameter variants, infinite spaces) doesn't just slow discovery of new content — it can also delay re-crawling of already-indexed pages whose content has changed, leaving stale versions in the index longer than necessary. See [Chapter 3, Section 6](chapter-03.md).

---

# 20. URL Parameters

Tracking, session, and sorting parameters (`?utm_source=`, `?sessionid=`, `?sort=price`) can generate large numbers of duplicate-content URL variants. Use canonical tags pointing to the parameter-free version, and avoid linking internally to parameterized URLs where a clean equivalent exists.

---

# 21. Common Indexing Issues

- Pages stuck at "Crawled - currently not indexed" due to perceived thin or duplicate content
- Conflicting signals — a page canonicalized to itself but blocked by robots.txt, or noindexed but still listed in the sitemap
- Soft 404s consuming index and crawl resources without providing real content
- JavaScript-rendered content missing from the index due to rendering delays
- Syndicated/duplicate content competing with (and sometimes outranking) the original source

---

# 22. Best Practices

- Use `noindex`, not `Disallow`, to reliably exclude pages from the index
- Keep canonical tags, sitemaps, and robots.txt rules consistent with each other — don't noindex a page you're also submitting in the sitemap
- Return genuine 404/410 status codes for removed content, never a soft 404
- Monitor the Index Coverage report as the primary indexing diagnostic, not just crawl stats
- Prioritize content quality and genuine helpfulness — indexing filters increasingly operate on quality, not just technical eligibility

---

# 23. Checklist

- [ ] Index Coverage report reviewed for unexpected exclusions
- [ ] `noindex` used deliberately and consistently with sitemap/canonical signals
- [ ] No soft 404s — genuinely missing content returns a real 404/410
- [ ] Duplicate content consolidated via canonical tags, not left to search-engine judgment
- [ ] Content quality reviewed against Helpful Content principles before publishing at scale

---

# Summary

Indexing is the quality gate between a successful crawl and search visibility — a page can be perfectly crawlable and still excluded from the index for being duplicate, thin, or low-value. Consistent, deliberate signals (canonical tags, noindex where genuinely intended, real 404s for removed content) paired with genuine content quality are what get a page reliably indexed, monitored through Search Console's Index Coverage report as the ground truth.

---

# Learning Outcomes

After completing this chapter, you will understand:

- How indexing works
- Why pages are excluded from the index
- Index coverage reports
- Duplicate content handling
- Canonicalization
- Index optimization techniques

---

# References

- Search Console Help: [Page indexing report](https://support.google.com/webmasters/answer/7440203) (formerly the Index Coverage report)
- Google Search Central: [How to Specify a Canonical with rel="canonical" and Other Methods](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

---

**Next:** Chapter 6 – Ranking
