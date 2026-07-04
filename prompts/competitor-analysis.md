# Competitor Analysis Prompts

Use with an LLM that has web access, or as a structured way to read competitor pages yourself. Pair with `seo-playbook entities --compare` for a data-grounded entity gap check.

## 1. Page-Type Backwards Analysis

```text
Here are the top 3-5 ranking pages for the query "{{target query}}": {{URLs or pasted
content}}. For each, identify: the page type (blog post, product page, tool, comparison,
landing page), the content structure (word count estimate, heading pattern), and what
user need it seems built to satisfy. Then tell me: is there a dominant page type Google
is rewarding for this query, and does my planned page ({{describe your page}}) match it?
```

**When to use:** Before writing a new page — confirms you're not writing a blog post for a query that wants a comparison table (see the `seo-sxo` skill for a deeper version of this analysis).

## 2. Content Gap Identification

```text
Compare this competitor page: {{competitor content}} against my page: {{my content}} on
the same topic. List: (1) subtopics they cover that I don't, (2) claims or statistics they
cite that I don't, (3) structural elements (FAQs, tables, comparison charts) they have that
I'm missing. Don't comment on writing quality — only coverage gaps.
```

**When to use:** Refreshing an underperforming page. Pair with `seo-playbook entities <mine.txt> --compare <theirs.txt>` for an automated entity-level version.

## 3. SERP Feature Audit

```text
For the query "{{query}}", what SERP features are likely present (Featured Snippet, PAA,
AI Overview, Image Pack, Video Carousel, Local Pack, Shopping results)? For each present
feature, what content format tends to win it, and does my current content have a real
shot at any of them?
```

**When to use:** Prioritizing which queries are worth investing extra optimization effort in.

## 4. Backlink Profile Angle (manual research prompt)

```text
I'm researching backlinks for {{competitor domain}} using {{tool name/data pasted}}. Based
on this data, what content or asset types seem to be earning them the most links (original
research, tools, guides, data visualizations)? Suggest 3 linkable-asset ideas for my site
in the same space that would appeal to the same linking domains.
```

**When to use:** Planning digital PR / linkable-asset content — see [Link Building Prompts](link-building.md).

## 5. Positioning Differentiation

```text
My competitors in {{niche}} are: {{list domains}}. Based on their homepage and about-page
messaging, what angle or promise do they all share? Suggest a differentiated positioning
angle for my site that doesn't just copy the category consensus.
```

**When to use:** Early-stage content strategy, before keyword-level work.
