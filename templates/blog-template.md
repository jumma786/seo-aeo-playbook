# Blog Post Template

A copy-paste starting point for a new blog post. For an automated version of this same structure (built from a keyword-clustered content brief), see `seo-playbook blog-scaffold` — see [`scripts/blog_generator.py`](../scripts/blog_generator.py) and the [Content Brief](../checklists/on-page.md) / [SEO Content Prompts](../prompts/seo-content.md).

---

```markdown
---
title: "[Primary Keyword]: [Compelling Angle] (30-60 characters)"
description: "[70-160 character meta description — an accurate, compelling preview, not keyword-stuffed]"
date: YYYY-MM-DD
author: [Author Name]
slug: primary-keyword-slug
---

# [Primary Keyword]: [Compelling Angle]

[Introduction — 150-225 words. Lead with the direct answer/claim before supporting
detail (see AEO Book, Chapter 7: AI Citations & Passage-Level Citability). State
what this post covers and who it's for.]

## [First H2 — a specific, scannable subtopic, not "Overview"]

[Content covering this subtopic. Lead with the direct point, then support it.
Target keywords for this section: keyword1, keyword2]

## [Second H2]

[Content...]

## [Third H2]

[Content...]

## Frequently Asked Questions

### [A real question a reader would actually ask, ending in "?"]

[A complete, self-contained 15-60 word answer that names its subject explicitly —
see scripts/faq_generator.py's validation criteria in the FAQ Template below.]

### [Second question]

[Answer]

## Summary / Key Takeaways

- [Bulleted recap of the 3-5 most important points]

<!-- Schema: generate matching Article + FAQPage JSON-LD with:
     seo-playbook schema article --headline "..." --author "..." --date-published "..."
     seo-playbook faq faq.json
-->
```

---

## Checklist before publishing

- [ ] Title is 30-60 characters and matches search intent for the primary keyword — [On-Page Checklist](../checklists/on-page.md)
- [ ] Meta description is 70-160 characters
- [ ] Exactly one H1, logical H2/H3 hierarchy
- [ ] At least one internal link to and from related content — `seo-playbook link-suggestions`
- [ ] FAQ answers are self-contained and 15-60 words each
- [ ] Article schema generated and validated — `seo-playbook schema validate`
