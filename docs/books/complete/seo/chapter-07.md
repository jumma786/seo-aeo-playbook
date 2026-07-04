# Chapter 7: Search Intent

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What is Search Intent?
3. Why Search Intent Matters
4. Types of Search Intent
5. Informational Intent
6. Navigational Intent
7. Transactional Intent
8. Commercial Investigation
9. Mixed Intent
10. User Journey
11. Query Classification
12. Keyword Intent Mapping
13. SERP Analysis
14. Content Matching
15. Featured Snippets
16. People Also Ask
17. AI Search Intent
18. Intent Optimization
19. Measuring Success
20. Common Mistakes
21. Best Practices
22. Checklist
23. Summary
24. References

---

# 1. Introduction

Search intent is the reason behind a user's search query. Understanding intent helps create content that satisfies user needs instead of simply targeting keywords. Modern search engines prioritize pages that best match the user's intent, ranking a technically weaker page that matches intent above a stronger page that doesn't.

---

# 2. What is Search Intent?

Search intent is the underlying goal a searcher is trying to accomplish — to learn something, find a specific site, compare options, or complete a purchase. Two queries can share keywords but carry entirely different intent ("running shoes" alone is ambiguous — informational research or ready-to-buy — while "buy running shoes size 10" is unambiguously transactional).

---

# 3. Why Search Intent Matters

A page that ranks for the right keyword but the wrong intent will underperform: high bounce rate, low dwell time, and eventual ranking decline as a search engine's behavioral signals reflect the mismatch. Matching content format to intent — not just topic to keyword — is one of the highest-leverage things a content strategy can get right, and it's a prerequisite for everything covered in [Chapter 9 (Content Optimization)](chapter-09.md).

---

# 4. Types of Search Intent

Search intent is typically classified into four categories, detailed in the sections that follow: **informational**, **navigational**, **transactional**, and **commercial investigation**. Some frameworks treat commercial investigation as a sub-type of transactional intent, since it precedes a purchase decision without being the purchase itself.

---

# 5. Informational Intent

The user wants to learn something, with no immediate intent to transact.

Examples:

- What is SEO?
- How does Google rank websites?
- SEO checklist

Informational queries are typically best served by comprehensive guides, definitions, tutorials, and FAQ content.

---

# 6. Navigational Intent

The user wants to visit a specific website or page they already have in mind.

Examples:

- GitHub
- Google Search Console
- Ahrefs login

Ranking for navigational queries about your own brand is usually straightforward; competing for navigational queries about someone else's brand is rarely a productive strategy.

---

# 7. Transactional Intent

The user is ready to take action — buy, sign up, download, or hire.

Examples:

- Buy SEO software
- Hire SEO consultant
- SEO agency near me

Transactional queries are best served by product pages, pricing pages, and clear calls to action — not long-form educational content that delays the action the searcher is already ready to take.

---

# 8. Commercial Investigation

The user is comparing options before making a decision — past pure research, not yet ready to commit.

Examples:

- Best SEO tools
- Ahrefs vs Semrush
- Best keyword research software

Comparison pages, "best of" roundups, and detailed reviews are the formats that typically win this intent — see the `seo-competitor-pages` skill for building comparison/alternatives pages specifically.

---

# 9. Mixed Intent

Some queries carry genuinely mixed or ambiguous intent, where the SERP itself shows a blend of content types (e.g., "SEO tools" surfacing both educational "what is" content and commercial "best tools" roundups). When intent is mixed, examine the actual SERP composition rather than guessing — the ranking pages are the ground truth for what a search engine believes the query wants.

---

# 10. User Journey

A single searcher often moves through multiple intents over time for the same broad topic — informational research, then commercial investigation, then transactional action. Content strategy should map coverage across this journey (see [Content Brief Prompts](../../../../prompts/seo-content.md) and `seo-playbook content-brief`) rather than only targeting the bottom-of-funnel transactional query.

---

# 11. Query Classification

Classifying a keyword's intent is usually done by combining query phrasing cues ("how to", "best", "buy", "near me", "vs") with direct SERP observation — the dominant content type ranking for a query is the most reliable intent signal available, more reliable than the query text alone.

---

# 12. Keyword Intent Mapping

Once classified, each keyword should be mapped to exactly one target page whose format matches that intent — informational keywords to guide/blog content, transactional keywords to product/service pages, commercial-investigation keywords to comparison content. `seo-playbook keyword-map suggest` automates the mechanical part of this mapping against existing pages.

---

# 13. SERP Analysis

Analyzing the current top-ranking pages for a target query — their content type, structure, and depth — is the most direct way to confirm intent before committing to a content format. See [Competitor Analysis Prompts](../../../../prompts/competitor-analysis.md) for a structured version of this analysis (also called SERP "backwards analysis").

---

# 14. Content Matching

Content matching means aligning not just topic but *format* to intent: a listicle for "best X" queries, a direct how-to for "how to X" queries, a comparison table for "X vs Y" queries. Matching format is often as important as matching topic — a technically excellent blog post will still underperform a simpler comparison page for a commercial-investigation query.

---

# 15. Featured Snippets

Featured Snippets predominantly win informational, question-phrased queries with a direct, extractable answer near the top of the content. Structuring content to lead with a direct answer (see [AEO Book, Chapter 7](../aeo/chapter-07.md)) improves snippet odds for informational intent specifically.

---

# 16. People Also Ask

The People Also Ask box surfaces related questions largely tied to informational intent, offering a direct signal of adjacent sub-topics and questions a comprehensive piece should address. Mining these questions is a practical, low-effort keyword and content-gap research technique — see [Content Gap Prompts](../../../../prompts/content-gap.md).

---

# 17. AI Search Intent

AI answer engines (ChatGPT Search, AI Overviews, Perplexity) tend to synthesize answers most readily for informational and commercial-investigation intent, where a direct, well-supported answer can be generated — transactional intent still tends to route to the actual product/service page or checkout flow rather than being synthesized. See the [AEO Book](../../aeo/README.md) for platform-specific detail.

---

# 18. Intent Optimization

- Confirm intent via live SERP composition before choosing a content format
- Match structure to intent (comparison tables, direct answers, product pages) not just topic
- Cover the full user journey for a topic area, not only the bottom-of-funnel query
- Revisit intent classification periodically — SERPs for a given query can shift intent over time (e.g., a query drifting from purely informational toward commercial as a market matures)

---

# 19. Measuring Success

Intent-match success is best measured through engagement signals (bounce rate, dwell time, scroll depth) alongside ranking position — a page ranking well but with poor engagement metrics is a strong signal of an intent mismatch worth investigating, even before a ranking drop appears.

---

# 20. Common Mistakes

- Writing a blog post for a query the SERP shows is dominated by product/comparison pages (or vice versa)
- Targeting only the bottom-of-funnel transactional query while ignoring the informational research stage that precedes it
- Assuming intent from query phrasing alone without checking the actual SERP
- Treating commercial-investigation queries as purely transactional, missing the comparison-content format they actually reward

---

# 21. Best Practices

- Classify intent from live SERP composition, not guesswork
- Map each keyword to one page whose format matches its intent — `seo-playbook keyword-map suggest`
- Cover informational, commercial-investigation, and transactional stages for core topics, not just one
- Revisit intent classification periodically as SERPs evolve

---

# 22. Checklist

- [ ] Target query's actual SERP composition checked before choosing a content format
- [ ] Content format matches intent (guide vs. comparison vs. product page), not just topic
- [ ] Each keyword mapped to exactly one target page — `seo-playbook keyword-map audit` catches cannibalization from mismatched mapping
- [ ] Engagement metrics (bounce rate, dwell time) reviewed as an intent-match signal, not just rank position
- [ ] Full user journey (informational → commercial → transactional) covered for core topics, not just bottom-of-funnel queries

---

# Summary

Search intent is the lens every other SEO discipline in this book operates through — the right keyword, the right technical setup, and the right backlinks still underperform if the content format doesn't match what a searcher (and the SERP) actually expects for that query. Classifying intent from real SERP composition, matching content format accordingly, and covering the full user journey for a topic is what turns keyword research into content that actually satisfies demand.

---

# Learning Outcomes

After completing this chapter, you will understand:

- Search intent classification
- Intent-based keyword research
- SERP analysis
- Content optimization for intent
- AI search intent strategies

---

# References

- Google Search Quality Rater Guidelines: Needs Met Rating
- Google Search Central: Understanding Search Intent

---

**Next:** Chapter 8 – Keyword Research
