# Technical SEO Prompts

For interpreting technical findings and drafting configuration — see the [Technical SEO Checklist](../checklists/technical-seo.md), and `seo-playbook robots`/`sitemap`/`schema validate`/`page-speed` for the mechanical checks these prompts help you act on.

## 1. robots.txt Rule Review

```
Here is my current robots.txt: {{paste content}}. Explain in plain language what each
rule actually does, and flag anything that looks like it might unintentionally block a
crawler I'd want indexing content (including AI crawlers like GPTBot, PerplexityBot,
ClaudeBot — see `seo-playbook llms audit-crawlers` for an automated version of this check).
```

**When to use:** Reviewing or inheriting a robots.txt you didn't write yourself.

## 2. Redirect Chain Explanation

```
Here's a redirect chain I found: {{paste chain, e.g. "A -> B -> C -> D"}}. Explain why
this is a problem (or isn't), and what the correct single-hop redirect should be.
```

**When to use:** Cleaning up redirect chains found via `seo-playbook check-links`.

## 3. Render-Blocking Resource Triage

```
Here's a list of render-blocking scripts/stylesheets flagged on my page:
{{paste output of `seo-playbook page-speed`}}. For each, suggest whether it's a
candidate for `async`, `defer`, moving to the end of `<body>`, or inlining as critical
CSS — based on what the resource likely does (analytics, fonts, core layout CSS, etc.).
```

**When to use:** Turning a page-speed audit's render-blocking findings into concrete fixes.

## 4. Faceted Navigation Crawl Budget Plan

```
My site has faceted navigation with these filter dimensions: {{list, e.g. "color, size,
price range, brand"}}. Which filter combinations are worth being indexable (real search
demand) vs. should be noindexed or blocked via robots to avoid crawl budget waste?
```

**When to use:** E-commerce or large catalog sites with combinatorial URL explosion.

## 5. Migration Redirect Map Review

```
Here is my old-URL to new-URL redirect map: {{paste mapping}}. Flag any old URL that's
missing a mapping, any many-to-one redirect that might be conflating distinct pages'
authority, and any redirect chain (old URL redirecting to another redirect, not the
final destination).
```

**When to use:** QA-ing a redirect map before a domain or URL-structure migration — pairs with the [Launch Checklist](../checklists/launch-checklist.md).
