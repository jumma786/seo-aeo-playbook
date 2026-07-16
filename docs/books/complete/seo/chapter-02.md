# Chapter 2: How Search Engines Work

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What is a Search Engine?
3. Major Search Engines
4. Search Engine Architecture
5. Crawlers (Spiders/Bots)
6. Crawl Budget
7. Robots.txt
8. XML Sitemaps
9. Rendering
10. JavaScript Rendering
11. Indexing
12. Canonicalization
13. Ranking Algorithms
14. Ranking Signals
15. Search Intent
16. SERP Features
17. Featured Snippets
18. Knowledge Panels
19. AI Overviews
20. Freshness Signals
21. Spam Detection
22. Helpful Content Systems
23. Core Web Vitals
24. Common Crawling Issues
25. Best Practices
26. Summary
27. References

---

# 1. Introduction

Search engines help users discover information on the web by crawling websites, processing content, storing it in an index, and ranking pages based on hundreds of signals.

The process can be simplified into four major stages:

1. Discover
2. Crawl
3. Index
4. Rank

Understanding this workflow is the foundation of technical SEO and modern AI search optimization — every chapter after this one in the SEO Book goes deep on one stage or one signal within it.

---

# 2. What is a Search Engine?

A search engine is a software system that discovers, stores, organizes, and retrieves web pages based on a user's query. It combines a crawler (to discover content), an index (to store it), and a ranking algorithm (to order results) into a single retrieval pipeline.

---

# 3. Major Search Engines

| Engine | Type | Notes |
|---|---|---|
| Google | Traditional + AI | Dominant global market share; AI Overviews layered on top of classic results |
| Bing | Traditional + AI | Powers Yahoo and, in part, Microsoft Copilot |
| DuckDuckGo | Traditional, privacy-focused | No personalized tracking |
| Brave Search | Traditional, independent index | Not solely reliant on Bing/Google data |
| ChatGPT Search | AI-native | Conversational retrieval, cites sources inline |
| Perplexity | AI-native | Positions itself as an "answer engine" first |
| Gemini | AI-native | Deep integration with Google's Knowledge Graph and Search index |
| Claude | AI-native | Uses web search as a tool rather than a dedicated search product |

The [AEO Book](../aeo/README.md) covers the AI-native engines individually in depth.

---

# 4. Search Engine Architecture

A search engine's architecture typically consists of: a crawler/fetcher, a renderer (for JavaScript-dependent content), an indexer, a ranking system, and a serving layer that assembles the final results page (including non-link SERP features). Each component can independently fail a page — for example, a page can be crawled successfully but fail to render its main content, and therefore be indexed with the wrong (or missing) content.

---

# 5. Crawlers (Spiders/Bots)

Crawlers (also called spiders or bots) are automated programs that fetch pages by following links and reading sitemaps. Googlebot and Bingbot are the two most consequential for traditional search; a growing list of AI crawlers (GPTBot, PerplexityBot, ClaudeBot, and others) now also crawl for training data and live retrieval. See [Chapter 3](chapter-03.md) for a full treatment of crawling.

---

# 6. Crawl Budget

Crawl budget is the finite amount of crawling attention a search engine allocates to a given site, based on its perceived value and server capacity. Large or frequently-changing sites need to actively manage crawl budget to ensure priority pages are crawled promptly; see [Chapter 3, Section 6](chapter-03.md).

---

# 7. Robots.txt

`robots.txt` is a plain-text file at a site's root that tells crawlers which paths they may or may not access. It governs *permission*, not visibility — a disallowed page can still be indexed (without its content) if other pages link to it. `scripts/robots_generator.py` in this repository generates and validates robots.txt files programmatically.

---

# 8. XML Sitemaps

An XML sitemap lists a site's URLs explicitly, helping crawlers discover pages that might otherwise be missed through link-following alone — especially useful for large or poorly-interlinked sites. `scripts/sitemap_generator.py` in this repository generates sitemaps (including automatic splitting for sites over 50,000 URLs).

---

# 9. Rendering

Rendering converts a page's HTML, CSS, and JavaScript into the content a browser (or crawler) actually displays. Content that only appears after client-side JavaScript executes is at risk of being missed or delayed in indexing. See [Chapter 4](chapter-04.md).

---

# 10. JavaScript Rendering

Google renders JavaScript in a second wave after initial crawling, using a headless Chromium instance — but this second wave can be delayed by hours or days on large sites, and many other crawlers (including most AI crawlers) render JavaScript far less reliably or not at all. See [Chapter 4, Section 11](chapter-04.md).

---

# 11. Indexing

Indexing is the process of analyzing and storing a crawled, rendered page so it becomes eligible to appear in search results. Not every crawled page gets indexed — duplicate, thin, or low-quality content is often excluded even after being successfully crawled. See [Chapter 5](chapter-05.md).

---

# 12. Canonicalization

Canonicalization is the process of choosing one authoritative URL among several that serve duplicate or near-duplicate content, consolidating ranking signals onto that single version. See [Chapter 5, Section 6](chapter-05.md).

---

# 13. Ranking Algorithms

Ranking algorithms evaluate indexed pages against a query and order them by predicted relevance and quality. Modern ranking systems (including Google's) combine hundreds of individual signals and machine-learned models rather than a single formula. See [Chapter 6](chapter-06.md).

---

# 14. Ranking Signals

Ranking signals span relevance (does this page match the query), authority (backlinks, entity trust), quality (E-E-A-T, content depth), and experience (page speed, mobile usability, Core Web Vitals). See [Chapter 6, Section 5](chapter-06.md).

---

# 15. Search Intent

Search intent — informational, navigational, transactional, or commercial-investigation — determines what *kind* of result a query rewards, independent of exact keyword matching. See [Chapter 7](chapter-07.md).

---

# 16. SERP Features

A search engine results page (SERP) is rarely just ten blue links anymore. Featured Snippets, Knowledge Panels, People Also Ask, Image/Video packs, Local Packs, and AI Overviews all compete for the same visual space and user attention.

---

# 17. Featured Snippets

A Featured Snippet lifts a short passage directly into a highlighted box above the standard results, usually for a well-phrased answer to a specific question. The same self-contained, answer-first writing that wins Featured Snippets tends to also perform well for AI Overview citation (see [AEO Book, Chapter 7](../aeo/chapter-07.md)).

---

# 18. Knowledge Panels

A Knowledge Panel is an information box (typically on the right side of desktop results) summarizing facts about an entity — a person, organization, or place — sourced from a knowledge graph like Google's. Strong entity signals and structured data increase the odds of qualifying for one. See [Chapter 10](chapter-10.md).

---

# 19. AI Overviews

AI Overviews place an AI-generated summary above traditional results for many queries, synthesizing and citing multiple sources. See [AEO Book, Chapter 4](../aeo/chapter-04.md).

---

# 20. Freshness Signals

Freshness signals help a search engine judge whether content reflects current information — most heavily weighted for genuinely time-sensitive queries (news, pricing, current events), less so for evergreen topics where an old but accurate page can still rank well.

---

# 21. Spam Detection

Spam detection systems (Google's SpamBrain and its predecessors) identify and demote manipulative tactics — keyword stuffing, cloaking, link schemes, scraped or auto-generated low-value content — that attempt to rank without providing genuine value.

---

# 22. Helpful Content Systems

Google's Helpful Content System evaluates whether content was created primarily for people (genuinely useful) or primarily to attract search traffic (thin, formulaic, or mass-produced with no real added value), demoting sites where the latter dominates.

---

# 23. Core Web Vitals

Core Web Vitals — LCP, INP, and CLS — are standardized metrics for loading speed, interaction responsiveness, and visual stability, used as page-experience ranking signals. See [Chapter 13](chapter-13.md).

---

# 24. Common Crawling Issues

- Accidental `robots.txt` disallow rules blocking priority sections
- Crawl budget wasted on faceted-navigation or parameter-URL explosions
- JavaScript-rendered content never reaching the index
- Broken internal links preventing discovery of deeper pages
- Server errors or timeouts during crawl attempts going unnoticed

---

# 25. Best Practices

- Keep the crawl → render → index → rank pipeline in mind when diagnosing any visibility issue — identify which stage is actually failing before attempting a fix
- Maintain an accurate, current XML sitemap and a deliberate (not default) robots.txt policy
- Verify JavaScript-dependent content is visible in rendered HTML, not just the initial source
- Monitor Search Console's Index Coverage and Crawl Stats reports on a recurring basis
- Track SERP feature presence (Featured Snippets, AI Overviews) for priority queries, not just blue-link position

---

# Summary

Every search engine, traditional or AI-native, runs the same underlying pipeline: discover, crawl, render, index, and rank. A failure at any stage — a blocked crawl path, a JavaScript rendering gap, a duplicate-content indexing conflict — prevents even excellent content from ever reaching the ranking stage. Understanding this pipeline end-to-end is what makes technical SEO diagnosis possible, and it's the foundation every later chapter in this book builds on.

---

# Learning Outcomes

After completing this chapter, you will understand:

- How search engines discover, crawl, render, index, and rank pages
- The role of robots.txt, sitemaps, and canonicalization in this pipeline
- How modern SERPs extend beyond ten blue links
- How AI search builds on, rather than replaces, this traditional pipeline

---

# References

- Google Search Central: [In-Depth Guide to How Google Search Works](https://developers.google.com/search/docs/fundamentals/how-search-works)
- Google Search Central: [Google Crawling and Indexing](https://developers.google.com/search/docs/crawling-indexing)

---

**Next:** Chapter 3 – Crawling
