# Chapter 6: Ranking

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What is Ranking?
3. Ranking vs Indexing
4. Ranking Algorithms
5. Ranking Signals
6. Relevance
7. Authority
8. Content Quality
9. Search Intent
10. E-E-A-T
11. User Experience
12. Core Web Vitals
13. Page Speed
14. Mobile-First Indexing
15. Structured Data
16. Internal Linking
17. External Links
18. Backlinks
19. Freshness
20. Topical Authority
21. Entity SEO
22. AI Ranking Signals
23. Helpful Content
24. Measuring Rankings
25. Common Ranking Issues
26. Best Practices
27. Summary
28. References

---

# 1. Introduction

Ranking is the process search engines use to determine the order in which indexed pages appear for a user's search query. Modern search engines evaluate hundreds of signals to identify the most relevant, trustworthy, and helpful results.

A higher ranking generally leads to greater visibility, increased organic traffic, and improved business outcomes.

---

# 2. What is Ranking?

Ranking happens at query time: from the full set of indexed pages that could plausibly match a query, a ranking system scores and orders them by predicted relevance and quality. Unlike indexing (a largely static, page-level decision), ranking position can shift per query, per user location, and over time as signals change.

Effective ranking depends on multiple factors, including:

- Relevance to the search query
- Content quality
- Website authority
- User experience
- Technical SEO
- E-E-A-T signals
- Search intent alignment
- Freshness of content

---

# 3. Ranking vs Indexing

Indexing asks "should this page be in the searchable database at all?" Ranking asks "given that it's in the database, where does it belong for this specific query, right now?" A page can be indexed but rank poorly (or not appear at all in the top results) for a given query if it's simply outcompeted — indexing is a prerequisite for ranking, not a guarantee of it.

---

# 4. Ranking Algorithms

Modern ranking systems (Google's core ranking system and its many sub-systems) combine hundreds of individual signals and machine-learned models rather than a single formula, and are updated continuously through both minor tweaks and named "core updates" that can meaningfully reshuffle results for certain query types or content categories.

---

# 5. Ranking Signals

Ranking signals broadly cluster into four categories, covered individually in the sections below: **relevance** (does this page match the query), **authority** (backlinks, entity trust, brand recognition), **quality** (E-E-A-T, content depth, Helpful Content standing), and **experience** (Core Web Vitals, mobile usability, intrusive interstitials).

---

# 6. Relevance

Relevance measures how well a page's content matches the meaning behind a query — not just exact keyword matches, but semantic and intent alignment (see [Chapter 7](chapter-07.md)). A page can use the exact query phrase and still rank poorly if it doesn't actually satisfy what the searcher wants.

---

# 7. Authority

Authority reflects how much a search engine trusts a site or page as a source for a given topic, built primarily through backlinks from other authoritative sources, brand recognition, and consistent entity presence across the web. Authority is topic-relative — a site can be highly authoritative for one subject and have none for an unrelated one.

---

# 8. Content Quality

Content quality spans depth, accuracy, originality, and genuine usefulness — the difference between a page that satisfies a search and one that merely targets it with the right keywords. See [Chapter 9](chapter-09.md).

---

# 9. Search Intent

A page that's technically excellent but matches the wrong intent (a product page for an informational query, or vice versa) will underperform regardless of its other strengths. See [Chapter 7](chapter-07.md) for the full intent framework.

---

# 10. E-E-A-T

Experience, Expertise, Authoritativeness, and Trustworthiness are the quality dimensions Google's human raters use to judge content, especially for YMYL topics — not a direct algorithmic ranking factor by name, but a strong influence on the systems and updates that are trained against those rater judgments. See [Chapter 12](chapter-12.md).

---

# 11. User Experience

Page experience — how easy a page is to use once a searcher arrives — includes speed, mobile usability, and the absence of intrusive interstitials. Poor UX doesn't just risk a ranking penalty directly; it also increases pogo-sticking (users bouncing back to the SERP), a behavioral signal search engines can observe.

---

# 12. Core Web Vitals

Core Web Vitals (LCP, INP, CLS) are Google's standardized, measurable proxies for loading speed, responsiveness, and visual stability — a concrete, quantified subset of the broader "user experience" ranking signal. See [Chapter 13](chapter-13.md).

---

# 13. Page Speed

Page speed affects both a direct ranking signal (via Core Web Vitals) and an indirect one (users abandon slow pages, increasing bounce rate). `seo-playbook page-speed` measures genuine time-to-first-byte and flags render-blocking resources contributing to slow loads.

---

# 14. Mobile-First Indexing

Under mobile-first indexing, the mobile version of a page — not the desktop version — is what Google actually crawls, indexes, and ranks against. Content, links, and structured data must be equivalent between mobile and desktop versions, or ranking-relevant signals present only on desktop will simply not be seen. See [Chapter 15](chapter-15.md).

---

# 15. Structured Data

Structured data doesn't directly boost ranking position, but it can unlock rich results (star ratings, FAQ dropdowns, breadcrumbs) that improve click-through rate at a given position — and reinforces entity and factual signals that feed into broader quality assessment. See [Chapter 14](chapter-14.md).

---

# 16. Internal Linking

Internal links distribute authority (link equity) from well-linked pages to others, and signal topical relationships that support topical authority. A page with strong external backlinks but no internal links pointing to it from relevant content is passing less of that authority onward than it could. See [Chapter 11](chapter-11.md).

---

# 17. External Links

Outbound links to authoritative, relevant sources can reinforce a page's own trustworthiness and topical context — the E-E-A-T "sources and citations" signal in practice — provided they're genuinely relevant, not link-farmed.

---

# 18. Backlinks

Backlinks (inbound links from other sites) remain one of the strongest authority signals, though quality and relevance matter far more than raw volume — a handful of links from genuinely authoritative, topically-relevant sites outweighs hundreds from low-quality or unrelated ones. See [Chapter 18](chapter-18.md).

---

# 19. Freshness

For queries with genuine time sensitivity, more recently published or meaningfully updated content is favored. For evergreen topics, freshness matters far less than depth and accuracy — an old, accurate, comprehensive page can outrank a newer but thinner one.

---

# 20. Topical Authority

Topical authority is the accumulated trust a site earns for a specific subject area through comprehensive, interlinked coverage over time — the practical outcome of the pillar-and-cluster architecture described in [Chapter 17](chapter-17.md). A single excellent page ranks on its own merits; a site with dozens of well-connected pages on the same topic area ranks with the added weight of demonstrated depth.

---

# 21. Entity SEO

Search engines increasingly rank based on entities (specific, disambiguated real-world things) and their relationships, not just keyword strings — allowing a page to rank for a concept even when it doesn't use the exact query phrasing. See [Chapter 10](chapter-10.md).

---

# 22. AI Ranking Signals

AI-powered ranking components (Google's use of large language models within its ranking systems, and AI Overviews' own separate retrieval-and-synthesis layer) increasingly weigh semantic relevance and passage-level citability alongside traditional signals. See the [AEO Book](../aeo/README.md) and [GEO Book](../geo/README.md) for how retrieval and generation work mechanically.

---

# 23. Helpful Content

Google's Helpful Content System acts as a broad, sitewide quality filter feeding into ranking — sites where low-value, search-engine-first content dominates can see ranking impact even on their genuinely good pages. See [Chapter 5, Section 15](chapter-05.md).

---

# 24. Measuring Rankings

Rank tracking (segmented by device and location, since results vary by both) shows position over time for priority keywords, but should always be paired with Search Console's actual click/impression data and business outcome metrics — a rank position alone doesn't confirm real traffic or conversion impact. See [Chapter 20](chapter-20.md).

---

# 25. Common Ranking Issues

- Mistaking a ranking drop for a technical/indexing issue when it's actually a relevance or quality gap (or vice versa)
- Over-indexing on backlink volume while neglecting on-page relevance and intent match
- Ignoring mobile-first indexing parity between mobile and desktop content
- Treating a single core update as the sole explanation for a ranking change without checking content/technical factors first
- Tracking rank position without connecting it to actual traffic or conversion data

---

# 26. Best Practices

- Build topical authority through comprehensive, interlinked coverage, not isolated pages
- Ensure mobile and desktop content parity given mobile-first indexing
- Treat Core Web Vitals as a real, measurable ranking input, not a vague "speed matters" gesture
- Earn backlinks through genuine authority-building, not manipulative link schemes
- Track rankings alongside real business outcomes, not as a standalone vanity metric

---

# Summary

Ranking is where relevance, authority, content quality, and user experience signals are weighed together, per query, to determine result order — a step downstream of both crawling and indexing, and dependent on all of the technical and content fundamentals covered elsewhere in this book. No single signal decides ranking alone; durable rankings come from consistently strong performance across all four signal categories, not from optimizing one at the expense of the others.

---

# Learning Outcomes

After completing this chapter, you will understand:

- How ranking works
- Key ranking signals
- The importance of relevance and authority
- Modern AI-influenced ranking factors
- Ranking optimization best practices

---

# References

- Google Search Central: How Search Algorithms Work
- Google Search Central: Core Updates Documentation

---

**Next:** Chapter 7 – Search Intent
