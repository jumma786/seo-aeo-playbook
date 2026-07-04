# On-Page SEO Prompts

For titles, meta descriptions, headings, and content structure. See the [On-Page SEO Checklist](../checklists/on-page.md) — `seo-playbook meta` and `seo-playbook audit` automate the mechanical length/structure checks these prompts feed into.

## 1. Title Tag Variants

```
Write 5 title tag options for a page about {{topic/product}}, targeting the keyword
"{{primary keyword}}". Each must be 30-60 characters, include the primary keyword near
the front, and read naturally (not keyword-stuffed). Vary the angle: one benefit-led, one
question-led, one number/list-led, one comparison-led, one direct/descriptive.
```

**When to use:** Drafting titles before running them through `seo-playbook meta --title "..."` for length validation.

## 2. Meta Description Draft

```
Write a meta description (70-160 characters) for a page about {{topic}}, summarizing:
{{one-sentence summary of the page's actual content}}. It should read as a genuine
preview, not an ad — accurately represent what's on the page, include the primary keyword
naturally if it fits without forcing it.
```

**When to use:** Pairs with `seo-playbook meta --description "..."` for length validation.

## 3. Heading Outline

```
I'm writing a page targeting "{{primary keyword}}" for a reader who wants {{describe
intent}}. Draft an H2/H3 heading outline (not full content) that covers the topic
comprehensively, with each heading phrased as a specific, scannable label — not generic
section names like "Overview" or "More Information."
```

**When to use:** Structuring a new page before writing full content — pairs with `seo-playbook content-brief` for word-count targets per section.

## 4. Thin Content Expansion

```
Here is a page that's currently {{word count}} words: {{paste content}}. It needs to reach
comprehensive depth on "{{topic}}" without padding. Identify 3-5 genuinely missing
subtopics or angles (not filler) that would extend it meaningfully.
```

**When to use:** When `seo-playbook audit` flags a page as thin content (under ~300 words).

## 5. Image Alt Text Batch

```
Here are image filenames/contexts from a page about {{topic}}: {{list, e.g. "hero-image:
person using product outdoors", "chart-1: bar chart of Q3 results"}}. Write descriptive,
specific alt text for each — describe what's actually shown, don't just repeat the target
keyword for every image.
```

**When to use:** Batch-fixing images `seo-playbook audit` flags as missing alt text.
