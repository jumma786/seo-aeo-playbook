# SEO Content Strategy Prompts

For content planning, briefs, and refreshes — distinct from mechanical on-page fixes (see [On-Page SEO Prompts](on-page-seo.md)). Pairs with `seo-playbook content-brief` and `seo-playbook blog-scaffold`.

## 1. Content Calendar Draft

```text
I publish content about {{topic area}} for {{audience}}, targeting {{cadence, e.g.
"2 posts per week"}}. Based on these keyword clusters: {{paste clusters}}, draft a
6-week content calendar — one topic per slot, ordered so foundational/pillar topics
come before topics that would naturally link back to them.
```

**When to use:** Turning clustered keywords into a publishing schedule.

## 2. Content Brief Enrichment

```text
Here is a mechanically generated content brief: {{paste output of
`seo-playbook content-brief`}}. Add: a suggested angle/thesis for the piece, 2-3
specific examples or case studies the writer could reference, and any competitor
content this should clearly differentiate from.
```

**When to use:** `seo-playbook content-brief` generates structure (sections, word counts, keywords) — this prompt adds the editorial judgment a mechanical tool can't.

## 3. Existing Content Refresh Plan

```text
This page was published {{date}} and covers {{topic}}: {{paste current content or
summary}}. What's likely outdated (statistics, screenshots, pricing, product names)?
What's still evergreen and shouldn't be touched? Give a specific refresh plan, not just
"update it."
```

**When to use:** Prioritizing content refreshes over always writing new pages.

## 4. Tone & Voice Consistency Check

```text
Here is our style guide summary: {{describe voice/tone}}. Here is a draft: {{paste
draft}}. Flag any sentences that drift from this voice (too formal/casual, inconsistent
person, inconsistent terminology for the same concept).
```

**When to use:** Multi-writer teams keeping a consistent voice across content.

## 5. Repurposing Plan

```text
Here is a long-form piece: {{paste or summarize}}. Suggest 3-4 ways to repurpose it into
shorter, distinct assets (a social thread, an FAQ section, a one-page summary, a
comparison table) without just copy-pasting excerpts.
```

**When to use:** Getting more mileage out of already-published cornerstone content.
