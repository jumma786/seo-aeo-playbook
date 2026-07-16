# Chapter 3: Crawling

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What is Crawling?
3. How Search Engine Crawlers Work
4. Googlebot
5. Bingbot
6. Crawl Budget
7. URL Discovery
8. Internal Links
9. XML Sitemaps
10. Robots.txt
11. Noindex vs Disallow
12. Crawl Frequency
13. JavaScript Crawling
14. Infinite Crawl Spaces
15. Duplicate URLs
16. Canonical URLs
17. HTTP Status Codes
18. Redirects
19. Log File Analysis
20. Crawl Optimization
21. Common Crawl Errors
22. Best Practices
23. Checklist
24. Summary
25. References

---

# 1. Introduction

Crawling is the process search engines use to discover web pages on the internet. Automated bots, commonly called crawlers or spiders, continuously follow links, read sitemaps, and revisit websites to find new or updated content.

Without crawling, a page cannot be indexed, and without indexing, it cannot appear in search results.

---

# 2. What is Crawling?

A crawler starts with a list of known URLs (a "crawl frontier") and follows hyperlinks to discover additional pages. It records important information about each page, including:

- URL
- Title
- Content
- Links
- Images
- Structured Data
- Response Status

This information is then passed to the indexing stage ([Chapter 5](chapter-05.md)) for further processing.

---

# 3. How Search Engine Crawlers Work

A crawler operates in a continuous loop: fetch a URL, parse its HTML, extract links and resources, add newly discovered URLs to the frontier, and repeat — prioritized by a scheduler that weighs a page's perceived importance, update frequency, and the site's overall crawl budget. Crawlers respect `robots.txt` rules and typically throttle request rate to avoid overloading a server (`Crawl-delay`, though Google ignores this directive specifically and instead paces itself based on server response health).

---

# 4. Googlebot

Googlebot is Google's primary crawler, operating in two effective passes: an initial HTML-only fetch, and a second "rendering" pass using a headless Chromium browser to execute JavaScript ([Chapter 4](chapter-04.md)). Googlebot crawls predominantly as a mobile user agent under mobile-first indexing, meaning the mobile version of a page is what actually gets evaluated.

---

# 5. Bingbot

Bingbot is Microsoft's crawler, powering both Bing search and, in part, Microsoft Copilot's grounding data. Bingbot's JavaScript rendering capability and crawl frequency have historically lagged Googlebot's, making server-rendered content and an accurate XML sitemap especially valuable for Bing visibility.

---

# 6. Crawl Budget

Crawl budget is the finite number of URLs a search engine is willing and able to crawl on a given site within a given timeframe — a function of both crawl demand (how much the search engine wants to crawl, based on perceived value) and crawl capacity (how much a site's server can handle without degrading). Large sites (tens of thousands of pages or more) need to actively manage crawl budget; small sites rarely hit its limits.

Common crawl budget drains:

- Faceted navigation generating near-infinite parameter combinations
- Soft 404s and redirect chains the crawler has to follow before finding real content
- Duplicate content across multiple URL variants
- Slow server response times reducing how much a crawler can fetch per visit

---

# 7. URL Discovery

Search engines discover new URLs primarily through: following links from already-known pages, reading XML sitemaps, and (for some engines) analyzing referrer data or directly submitted URLs (via Search Console's URL Inspection tool). A URL with no inbound links and no sitemap entry may never be discovered at all.

---

# 8. Internal Links

Internal links are the primary path crawlers use to discover pages beyond the homepage. A logical, shallow internal linking structure ([Chapter 11](chapter-11.md)) directly determines crawl efficiency — pages several clicks deep from the homepage are crawled less frequently and less thoroughly than pages near the top of the architecture.

---

# 9. XML Sitemaps

An XML sitemap explicitly lists a site's canonical URLs, supplementing link-based discovery — especially valuable for large sites, new sites with few inbound links, or sites with content behind forms/search that isn't otherwise linked. `scripts/sitemap_generator.py` in this repository generates sitemaps and automatically splits sets over the 50,000-URL protocol limit into a sitemap index; run it via `seo-playbook sitemap urls.txt output.xml`.

---

# 10. Robots.txt

`robots.txt` is a plain-text file at a site's root (`/robots.txt`) that tells crawlers which URL paths they may or may not request. It's a *permission* mechanism, not a privacy mechanism — a disallowed URL can still appear in search results (without its content) if other pages link to it, and the file itself is publicly readable. `scripts/robots_generator.py` generates and validates robots.txt rules, including a check for accidental sitewide blocks; run it via `seo-playbook robots output.txt --disallow /path/`.

---

# 11. Noindex vs Disallow

These are frequently confused but do different jobs:

| Directive | Where | Effect |
|---|---|---|
| `Disallow` (robots.txt) | Crawl-time | Prevents the page from being *crawled* at all — a search engine can't read a noindex tag on a page it's never allowed to fetch |
| `noindex` (meta tag or header) | Index-time | Allows crawling, but tells the search engine not to *index* the page |

To reliably remove a page from search results, use `noindex` and allow crawling (so the directive is seen) — using `Disallow` alone can leave a URL indexed with no snippet, since the crawler never sees the noindex instruction.

---

# 12. Crawl Frequency

Crawl frequency — how often a search engine revisits a given URL — scales with perceived importance and update frequency. Homepages and high-authority pages may be crawled multiple times per day; low-priority or rarely-updated pages may go weeks or months between crawls. Consistently fresh, frequently-linked-to content tends to earn more frequent crawling over time.

---

# 13. JavaScript Crawling

Crawlers must execute JavaScript to see content that's rendered client-side, which is slower and more resource-intensive than parsing static HTML. Googlebot handles this via a second rendering wave that can lag the initial crawl by hours to days on large sites; many other crawlers (including most AI crawlers) have far more limited JavaScript execution. See [Chapter 4](chapter-04.md) for the full rendering pipeline.

---

# 14. Infinite Crawl Spaces

An infinite crawl space is a set of URLs that can grow without bound — typically from faceted navigation, calendar/date-based URLs, or session/tracking parameters — trapping crawler attention on low-value, near-duplicate pages instead of real content. Mitigate with `robots.txt` disallow rules on low-value parameter patterns, canonical tags pointing filtered views back to the primary page, and `noindex` on thin facet combinations.

---

# 15. Duplicate URLs

The same content reachable via multiple URLs (with/without trailing slash, with/without `www`, with tracking parameters, via HTTP and HTTPS) fragments crawl budget and ranking signals across variants that should be treated as one page. See [Chapter 5, Section 7](chapter-05.md) for how this affects indexing specifically.

---

# 16. Canonical URLs

A canonical tag (`<link rel="canonical" href="...">`) declares which URL among duplicates or near-duplicates is the authoritative version, consolidating crawl and ranking signals onto it. Every page should have a self-referencing canonical by default — pointing to itself unless there's a genuine duplicate to consolidate with.

---

# 17. HTTP Status Codes

| Code | Meaning | Crawl Impact |
|---|---|---|
| 200 | OK | Normal — page crawled and eligible for indexing |
| 301 | Permanent redirect | Signals pass to the destination; update internal links to point directly at it over time |
| 302 | Temporary redirect | Treated as genuinely temporary — original URL's signals are not expected to transfer permanently |
| 404 | Not found | Expected for genuinely removed content; unexpected 404s on live pages are a crawl error |
| 410 | Gone | A stronger, deliberate signal than 404 for permanently removed content |
| 500/503 | Server error | Frequent server errors reduce crawl capacity and can cause temporary de-indexing |

---

# 18. Redirects

Redirects preserve link equity and user access when a URL changes. Best practice: use 301 (permanent) redirects for permanent moves, keep redirect chains to a single hop (A → B, not A → B → C), and update internal links to point directly at the final destination rather than relying on the redirect indefinitely. `seo-playbook check-links` audits a URL list or an HTML page for broken links and redirect chains.

---

# 19. Log File Analysis

Server log files record every request made to a site, including by crawlers — the only source of truth for exactly what Googlebot, Bingbot, and other crawlers actually requested, how often, and what status code they received. Log analysis reveals crawl budget waste (bots repeatedly hitting low-value URLs), crawl gaps (priority pages not being visited), and rendering issues (JavaScript-heavy pages that crawlers request but may not fully process) that Search Console's sampled data can miss.

---

# 20. Crawl Optimization

- Keep priority pages within a shallow click depth of the homepage ([Chapter 17](chapter-17.md))
- Maintain a clean, current XML sitemap covering only canonical, indexable URLs
- Block low-value infinite spaces (faceted navigation, session parameters) via `robots.txt` and canonical rules
- Fix redirect chains and broken links promptly — `seo-playbook check-links`
- Improve server response time so crawlers can fetch more per visit
- Review log files periodically to confirm crawl behavior matches expectations

---

# 21. Common Crawl Errors

- Accidental `Disallow: /` blocking the entire site or a major section
- Redirect chains and loops wasting crawl budget before reaching real content
- Server errors (5xx) during crawl attempts going unnoticed without log monitoring
- Soft 404s — pages returning HTTP 200 but displaying "not found" content, confusing crawlers about what's genuinely available
- Sitemaps listing non-canonical, redirected, or noindexed URLs

---

# 22. Best Practices

- Treat `robots.txt` as a deliberate, reviewed configuration, not a default left unexamined
- Keep XML sitemaps limited to canonical, indexable, 200-status URLs
- Use `noindex` (not `Disallow`) when the goal is removing a page from search results
- Fix redirect chains to a single hop and update internal links to match
- Monitor Search Console Crawl Stats and raw log files, not just crawl-rate assumptions

---

# 23. Checklist

- [ ] `robots.txt` reviewed for accidental blanket disallows
- [ ] XML sitemap present, valid, and limited to canonical URLs — `seo-playbook sitemap`
- [ ] No redirect chains longer than one hop — `seo-playbook check-links`
- [ ] `noindex` used (not `Disallow`) for pages that should be crawled but excluded from the index
- [ ] Faceted navigation and other infinite crawl spaces controlled via robots/canonical rules
- [ ] Server log files reviewed periodically for crawl errors and wasted crawl budget

---

# Summary

Crawling is the mechanical first step of the entire search visibility pipeline — a page that can't be crawled can never be indexed or ranked, regardless of its content quality. Managing crawl budget, maintaining accurate sitemaps and robots.txt rules, fixing redirect chains, and monitoring actual crawler behavior through log files are the foundational technical SEO disciplines everything else in this book depends on.

---

# Learning Outcomes

After completing this chapter, you will understand:

- How Googlebot discovers pages
- Crawl budget optimization
- Robots.txt best practices
- XML Sitemap usage
- Internal linking strategies
- Common crawling problems

---

# References

- Google: [Google Crawler (User Agent) Overview](https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers)
- Google: [How Google Interprets the robots.txt Specification](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)

---

**Next:** Chapter 4 – Rendering
