# SEO / AEO / GEO Playbook

A complete, practitioner-grade guide to search visibility — from crawling fundamentals through AI-generated answers — paired with a Python CLI toolkit that implements the practices the books describe.

## The Books

| Book | Chapters | Focus |
|---|---|---|
| [SEO Book](books/complete/seo/README.md) | 20 | Traditional search: crawling, indexing, ranking, on-page and technical SEO, local SEO, and analytics |
| [AEO Book](books/complete/aeo/README.md) | 10 | Answer Engine Optimization: ChatGPT, Google AI Overviews, Perplexity, Gemini, Claude, citations, and llms.txt |
| [GEO Book](books/complete/geo/README.md) | 8 | Generative Engine Optimization: knowledge graphs, entities, embeddings, vector search, and RAG |

The books build on each other and are best read in sequence: **SEO** establishes the foundation, **AEO** extends it into AI answer engines, and **GEO** goes one layer deeper into the retrieval technology that makes every AEO tactic work mechanically. See the full [series overview](books/README.md) for the complete reading order.

## The CLI Toolkit

Every practice documented in the books has a corresponding command in the `seo-playbook` CLI — schema generation and validation, sitemap/robots.txt generation, keyword clustering and mapping, entity extraction, internal link suggestions, page speed and site audits, llms.txt generation and AI crawler auditing, content briefs, FAQ generation, and governed local-SEO page templates.

```bash
pip install -e .
seo-playbook --help
```

See the [CLI Reference](cli-reference.md) for the full command list.

## Status

All three books are complete (38 chapters total) and all 24 CLI commands are implemented with full test coverage. Canonical book location: `docs/books/complete/{seo,aeo,geo}/chapter-XX.md`.

## Contributing

This is an open-source project — contributions, corrections, and new tooling are welcome. See the repository [README](https://github.com/jumma786/seo-aeo-playbook) for more.
