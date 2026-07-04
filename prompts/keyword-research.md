# Keyword Research Prompts

Paste these into an LLM with web/search access (or pair the output with `seo-playbook cluster` and `seo-playbook keyword-map suggest` for the mechanical parts). See [SEO Book, Chapter 8: Keyword Research](../docs/books/complete/seo/chapter-08.md).

## 1. Seed Expansion

```text
I run a website about {{topic/industry}}, targeting {{audience}}. Generate 40-60 keyword
ideas a real searcher in this space would use, covering:
- Informational queries ("what is", "how to", "why")
- Commercial-investigation queries ("best", "vs", "review", "alternative to")
- Transactional queries (buying/signup intent)
- Long-tail variants (4+ words)

For each keyword, tag its likely search intent (informational / commercial / transactional
/ navigational). Output as a Markdown table: Keyword | Intent | Est. Difficulty (guess: low/med/high).
```

**When to use:** Starting keyword research for a new topic area or site section.

## 2. Question Mining

```text
List the 20 most common questions people ask about {{topic}}, phrased exactly as a person
would type or speak them (not keyword-stuffed). Group them into: Definition questions,
Comparison questions, How-to questions, Troubleshooting questions, and "Is it worth it"
questions. These will become FAQ content and PAA targets.
```

**When to use:** Building an FAQ section or targeting Featured Snippets / AI Overviews — feed the output into `seo-playbook faq` once you've written real answers.

## 3. Intent Classification for an Existing List

```text
Here is a list of keywords: {{paste list}}. For each one, classify search intent as
Informational, Commercial, Transactional, or Navigational, and note whether the SERP for
that intent is typically dominated by blog content, product/category pages, tools, or
comparison pages. Flag any keyword where the phrasing is ambiguous between two intents.
```

**When to use:** Before assigning keywords to page types, to avoid writing a blog post for a keyword that actually wants a product page (or vice versa).

## 4. Keyword-to-Cluster Naming

```text
I clustered these keywords by lexical similarity: {{paste clusters, e.g. from
`seo-playbook cluster keywords.txt`}}. For each cluster, suggest a clear H2-level section
title that a single page could rank for, and flag any cluster that's actually broad enough
to deserve its own dedicated page rather than a subsection.
```

**When to use:** After running `seo-playbook cluster`, to turn raw clusters into a content outline (pairs well with `seo-playbook content-brief`).

## 5. Competitor Keyword Gap

```text
My site targets these keywords: {{list}}. A competitor at {{competitor URL}} appears to
rank for similar topics. Based on their visible page titles, headings, and on-page content
(not scraped rank data), what topics or subtopics do they seem to cover that I don't?
```

**When to use:** Pair with [Competitor Analysis Prompts](competitor-analysis.md) and `seo-playbook entities` (with `--compare`) for a data-grounded version of the same question.
