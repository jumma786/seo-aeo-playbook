# Pillar Page Template

A copy-paste starting point for a pillar page — a comprehensive hub page covering a broad topic, linking out to narrower cluster pages that each cover a specific subtopic in depth. See [SEO Book, Chapter 17, Section 4: The Pillar-and-Cluster Model](../docs/books/complete/seo/chapter-17.md) and `seo-playbook cluster`/`content-brief` for building the underlying keyword clusters.

---

```markdown
---
title: "The Complete Guide to [Broad Topic] (30-60 characters)"
description: "[70-160 character meta description summarizing the full scope]"
---

# The Complete Guide to [Broad Topic]

[300-500 word comprehensive introduction establishing why this topic matters,
who it's for, and what the guide covers — this section itself should be
substantial enough to stand on its own, not just a table of contents.]

## What is [Broad Topic]?

[Foundational definition/overview section — the "101" level content a
newcomer needs before the deeper cluster topics make sense.]

## [Cluster Subtopic 1]

[A substantial overview of this subtopic (300-500 words) with a clear link
out to the full dedicated cluster page: "Read our complete guide to
[Subtopic 1]" → /cluster-page-1]

## [Cluster Subtopic 2]

[Same pattern — overview + link to /cluster-page-2]

## [Cluster Subtopic 3]

[Same pattern — overview + link to /cluster-page-3]

## [Cluster Subtopic N]

[Repeat for every subtopic in the cluster.]

## Frequently Asked Questions

[3-5 high-level questions about the broad topic — see the FAQ Template for
answer criteria.]

## Related Resources

[Links to every cluster page, plus any genuinely relevant external
authoritative sources.]
```

---

## How to build the cluster this pillar page anchors

1. Expand seed keywords into a full list — see [Keyword Research Prompts](../prompts/keyword-research.md)
2. Cluster them by topical similarity: `seo-playbook cluster keywords.txt`
3. Each resulting cluster becomes one dedicated cluster page, linked from this pillar
4. Generate a content brief per cluster page: `seo-playbook content-brief`
5. Once all cluster pages exist, audit for orphans and missing cross-links: `seo-playbook link-suggestions`

## Checklist

- [ ] Pillar page links out to every cluster page in the topic
- [ ] Every cluster page links back to the pillar (and to sibling cluster pages where relevant)
- [ ] Pillar page itself is substantive (500+ words minimum), not just a linked table of contents
- [ ] No orphan cluster pages — `seo-playbook link-suggestions`
