# Schema Markup Prompts

For drafting the *content* that goes into structured data — `seo-playbook schema article|faq` and `scripts/schema_generator.py` handle the actual JSON-LD generation and validation. See [SEO Book, Chapter 14: Structured Data & Schema Markup](../docs/books/complete/seo/chapter-14.md).

## 1. FAQPage Candidate Extraction

```text
Here is a page's content: {{paste content}}. Extract 4-6 genuine question/answer pairs
suitable for FAQPage schema — the question must be something a real user would ask (not
invented to hit a keyword), and the answer must be a complete, self-contained, 15-60 word
statement that names its subject explicitly (no "it" with no antecedent).
```

**When to use:** Feed the output directly into `seo-playbook faq`, which validates exactly these citability criteria and generates both the Markdown and the schema.

## 2. Article Metadata Extraction

```text
Here is a draft article: {{paste draft}}. Extract: a headline (30-60 chars), the author
name, and today's date as the publish date. If the article references an organization as
publisher, extract that name too.
```

**When to use:** Feed directly into `seo-playbook schema article --headline "..." --author "..." --date-published "..."`.

## 3. Product Schema Fact-Check

```text
Here is product schema I'm about to publish: {{paste JSON-LD or key fields}}. Cross-check
against this product page content: {{paste page content}}. Flag any mismatch — price,
availability, rating — between what the schema claims and what the visible page says.
Mismatched schema and visible content is a Google guidelines violation.
```

**When to use:** Pre-publish schema/content parity check — `seo-playbook schema validate` checks structural correctness but not parity with visible content.

## 4. LocalBusiness Field Completeness

```text
Here is what I know about this business location: {{paste available details}}. What
LocalBusiness schema fields (name, address, telephone, openingHours, priceRange,
geo coordinates) am I missing that I should go collect before publishing?
```

**When to use:** Before running `seo-playbook location-pages`, which requires complete NAP as a quality gate.

## 5. Breadcrumb Path Draft

```text
Here is my site's category structure: {{describe or paste nav}}. For a page at
{{page URL/topic}}, what's the correct breadcrumb path from the homepage, using the
actual category names as they appear in navigation (not invented labels)?
```

**When to use:** Feeding into `generate_breadcrumb_schema()` (see `scripts/schema_generator.py`).
