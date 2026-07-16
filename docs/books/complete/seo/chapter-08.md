# Chapter 8: Keyword Research

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What is Keyword Research?
3. Why Keyword Research Matters
4. Search Intent
5. Keyword Types
6. Short-Tail Keywords
7. Long-Tail Keywords
8. Seed Keywords
9. Primary Keywords
10. Secondary Keywords
11. Semantic Keywords
12. Entity-Based SEO
13. Search Volume
14. Keyword Difficulty
15. Cost Per Click (CPC)
16. Competitor Keyword Research
17. Keyword Gap Analysis
18. Keyword Clustering
19. Topic Clusters
20. Keyword Mapping
21. Local Keywords
22. International Keywords
23. AI Keyword Research
24. Keyword Research Tools
25. Best Practices
26. Checklist
27. Summary
28. References

---

# 1. Introduction

Keyword research is the process of discovering the words and phrases people use when searching online. It forms the foundation of every successful SEO strategy by helping you create content that matches user intent and attracts relevant organic traffic.

---

# 2. What is Keyword Research?

Keyword research starts from a small set of seed terms describing your topic or business, and expands outward — through search engine suggestions, competitor analysis, and question mining — into a comprehensive map of what your audience actually searches for, each phrase tagged with its likely intent ([Chapter 7](chapter-07.md)) and estimated demand.

---

# 3. Why Keyword Research Matters

Effective keyword research helps you:

- Understand your audience
- Discover search demand
- Create targeted content
- Improve search rankings
- Increase qualified traffic
- Identify content opportunities
- Build topical authority

Without it, content strategy becomes guesswork — publishing based on internal assumptions about what matters, rather than evidence of what people are actually searching for.

---

# 4. Search Intent

Every keyword carries an intent — informational, navigational, transactional, or commercial-investigation — and that intent should determine what kind of page you build to target it, not just what words appear in the copy. See [Chapter 7](chapter-07.md) for the full framework.

---

# 5. Keyword Types

Keywords are typically classified along two axes: length/specificity (short-tail vs. long-tail) and funnel position (seed, primary, secondary, semantic). The sections below cover each.

---

# 6. Short-Tail Keywords

Short-tail (or "head") keywords are broad, typically one to two words ("shoes," "SEO"), carrying high search volume but also high competition and ambiguous intent. They're useful for understanding a market's scale, but rarely a realistic primary target for a specific page.

---

# 7. Long-Tail Keywords

Long-tail keywords are longer, more specific phrases (four or more words, e.g., "best trail running shoes for wide feet") — individually lower volume, but collectively representing the majority of search traffic, with clearer intent and typically lower competition. Long-tail coverage compounds: dozens of well-targeted long-tail pages often outperform chasing a single high-volume head term.

---

# 8. Seed Keywords

Seed keywords are the small set of broad, foundational terms that describe your core business or topic area, used as the starting point for expansion into a full keyword list — "running shoes" as a seed might expand into hundreds of long-tail variants across use case, brand, and comparison angles.

---

# 9. Primary Keywords

A primary keyword is the single main term a specific page is built to target — the one used in the title, the primary heading, and the URL. Every page should have exactly one primary keyword to avoid diluting focus (and to avoid cannibalizing another page targeting the same term).

---

# 10. Secondary Keywords

Secondary keywords are closely related terms a page can also reasonably rank for as a byproduct of thoroughly covering its primary topic — supporting subtopics, synonyms, and related questions woven naturally into the content rather than treated as separate targets.

---

# 11. Semantic Keywords

Semantic keywords are terms and concepts related in meaning to the primary keyword, even without sharing exact words — covering them signals topical depth to both traditional semantic search systems and AI retrieval. See the [GEO Book, Chapter 4: Semantic Search](../geo/chapter-04.md) for how this matching works mechanically.

---

# 12. Entity-Based SEO

Beyond keyword strings, modern search increasingly reasons about entities — specific, disambiguated people, places, organizations, and concepts. Keyword research increasingly overlaps with entity research: which named entities (competitors, technologies, industry figures) should a comprehensive piece mention? See [Chapter 10](chapter-10.md) and `seo-playbook entities`.

---

# 13. Search Volume

Search volume estimates how often a keyword is searched over a given period, typically monthly. It's a useful prioritization signal but an imprecise one — estimates vary meaningfully between tools, and zero-reported-volume long-tail keywords can still collectively drive substantial traffic.

---

# 14. Keyword Difficulty

Keyword difficulty scores estimate how hard it would be to rank on the first page for a term, usually derived from the authority of currently-ranking pages. Use difficulty as a relative prioritization signal alongside your own site's current authority — a "hard" keyword for a new site may be perfectly reasonable for an established one.

---

# 15. Cost Per Click (CPC)

CPC — what advertisers pay per click in paid search for a given keyword — is a useful proxy for commercial value even for organic-only strategies: a high CPC signals a keyword sits close to a purchase decision, often correlating with commercial-investigation or transactional intent.

---

# 16. Competitor Keyword Research

Analyzing which keywords competing pages rank for reveals demand you may not have discovered from your own seed terms — see [Competitor Analysis Prompts](https://github.com/jumma786/seo-aeo-playbook/blob/main/prompts/competitor-analysis.md) for structured prompts covering this analysis.

---

# 17. Keyword Gap Analysis

A keyword gap analysis compares your own keyword coverage against competitors to surface terms they rank for that you don't — see [Content Gap Prompts](https://github.com/jumma786/seo-aeo-playbook/blob/main/prompts/content-gap.md), and `seo-playbook entities --compare` for the entity-level equivalent.

---

# 18. Keyword Clustering

Keyword clustering groups related keywords that should be targeted by a single page rather than split across several thin, competing ones — reducing keyword cannibalization risk and concentrating ranking signal. `scripts/keyword_cluster.py` in this repository clusters keywords by lexical token-overlap similarity; run it via `seo-playbook cluster keywords.txt`.

---

# 19. Topic Clusters

Topic clusters extend keyword clustering into full content architecture: a pillar page comprehensively covering a broad topic, linked to narrower cluster pages each covering a specific keyword cluster in depth. See [Chapter 17, Section 4](chapter-17.md) for the pillar-and-cluster architecture this produces.

---

# 20. Keyword Mapping

Keyword mapping assigns each keyword (or cluster) to exactly one target URL, prevent multiple pages from competing for the same term (keyword cannibalization). `seo-playbook keyword-map audit` checks an existing mapping for cannibalization; `keyword-map suggest` recommends a target page for unmapped keywords based on title similarity.

---

# 21. Local Keywords

Local keywords include geographic modifiers ("near me," a city or neighborhood name) signaling local intent, requiring location-specific landing pages rather than a single generic page attempting to rank everywhere at once. See [Chapter 19](chapter-19.md) and `seo-playbook location-pages`/`service-pages`.

---

# 22. International Keywords

Keyword research must be repeated per target language and region, not simply translated — search behavior, phrasing, and even the dominant search engine can differ meaningfully by market. See [Chapter 16](chapter-16.md) for hreflang and international targeting.

---

# 23. AI Keyword Research

AI tools can accelerate seed expansion, question mining, and intent classification (see [Keyword Research Prompts](https://github.com/jumma786/seo-aeo-playbook/blob/main/prompts/keyword-research.md)), but should be treated as a first-draft generator, not a replacement for checking real SERP composition and actual search demand data.

---

# 24. Keyword Research Tools

Beyond dedicated commercial keyword tools, this repository's own `seo-playbook cluster` (lexical clustering), `seo-playbook keyword-map` (mapping and cannibalization audit), and the `seo-cluster` skill (SERP-overlap-based clustering) provide a free, scriptable starting point for the mechanical parts of keyword organization.

---

# 25. Best Practices

- Start from real seed terms grounded in your actual business or content area, not guesses
- Classify intent for every keyword before assigning it to a page format
- Cluster related keywords to a single page rather than splitting them across near-duplicates
- Map every keyword to exactly one target page and audit for cannibalization periodically
- Treat search volume and difficulty as prioritization inputs, not absolute rankings of what to pursue

---

# 26. Checklist

- [ ] Seed keywords expanded into a comprehensive list covering informational, commercial, and transactional intent
- [ ] Every keyword classified by intent before content format is chosen
- [ ] Related keywords clustered to avoid splitting a topic across competing pages — `seo-playbook cluster`
- [ ] Keyword-to-URL mapping maintained and audited for cannibalization — `seo-playbook keyword-map audit`
- [ ] Competitor keyword and entity gaps reviewed periodically

---

# Summary

Keyword research turns guesswork about content strategy into evidence: what people actually search for, classified by intent, clustered to avoid cannibalization, and mapped one-to-one against target pages. It's the input every later content and architecture decision in this book depends on — [Chapter 9](chapter-09.md) covers what to do with a keyword once it's mapped to a page.

---

# Learning Outcomes

After completing this chapter, you will understand:

- Keyword types
- Search intent mapping
- Keyword clustering
- Competitor analysis
- AI-assisted keyword research
- Keyword strategy development

---

# References

- Google Ads Help: [Use Keyword Planner](https://support.google.com/google-ads/answer/7337243)
- Google Search Central: [Get started with Google Trends](https://developers.google.com/search/docs/monitor-debug/trends-start)

---

**Next:** Chapter 9 – Content Optimization
