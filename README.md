<div align="center">

# SEO / AEO / GEO Playbook

**A practitioner-grade guide to search visibility — and a tested Python toolkit that implements it.**

Rank on Google. Get cited by ChatGPT, AI Overviews, Gemini, Claude, and Perplexity.

[![Docs](https://img.shields.io/badge/docs-live-2ea44f)](https://jumma786.github.io/seo-aeo-playbook/)
[![Markdown](https://github.com/jumma786/seo-aeo-playbook/actions/workflows/markdown.yml/badge.svg)](https://github.com/jumma786/seo-aeo-playbook/actions/workflows/markdown.yml)
[![Tests](https://img.shields.io/badge/tests-483%20passing-2ea44f)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[**Read the docs**](https://jumma786.github.io/seo-aeo-playbook/) · [**CLI reference**](docs/cli-reference.md) · [**Start with the SEO Book**](docs/books/complete/seo/README.md)

</div>

---

## Why this exists

Ranking on Google is no longer the whole job. The same content now has to be **retrievable, citable, and structurally unambiguous** to answer engines that synthesize responses instead of returning ten blue links.

Most SEO resources give you prose you can't execute, or tools that don't explain themselves. This repository is deliberately both halves:

- **38 chapters** across three books that explain the mechanics — not tips, but how crawling, indexing, ranking, retrieval, and citation actually work.
- **A tested Python toolkit** — 22 CLI commands and a 25-endpoint HTTP API — that implements the practices those chapters describe.

Every chapter points at the command that automates it. Every command traces back to the chapter that justifies it.

## Quick start

```bash
git clone https://github.com/jumma786/seo-aeo-playbook.git
cd seo-aeo-playbook
pip install -e .

seo-playbook --help
```

Audit a live page in one command:

```bash
seo-playbook audit https://example.com
```

A few more of the 22 commands:

```bash
# Scaffold a project config that other commands read defaults from
seo-playbook init --brand "Example Corp" --domain example.com

# Generate validated Schema.org JSON-LD
seo-playbook schema article --headline "..." --author "..." --date-published 2026-01-15

# Group keywords into topic clusters, then find cannibalization
seo-playbook cluster keywords.txt
seo-playbook keyword-map audit mapping.json

# Score passages for AI-citation readiness (GEO Ch. 7 methodology)
seo-playbook geo-score content.md

# SEO + schema + performance across many URLs, one fetch per page
seo-playbook site-audit urls.txt
```

See the [CLI reference](docs/cli-reference.md) for all 22 commands and their options.

## What's inside

| Component | Status | Location |
|---|---|---|
| **SEO Book** — 20 chapters | Complete | [`docs/books/complete/seo/`](docs/books/complete/seo/README.md) |
| **AEO Book** — 10 chapters | Complete | [`docs/books/complete/aeo/`](docs/books/complete/aeo/README.md) |
| **GEO Book** — 8 chapters | Complete | [`docs/books/complete/geo/`](docs/books/complete/geo/README.md) |
| **CLI** — 22 commands | Complete, tested | [`cli/`](cli/) |
| **Toolkit** — 24 modules | Complete, tested | [`scripts/`](scripts/) |
| **HTTP API** — 25 endpoints | Complete, tested | [`api/`](api/) |
| **Documentation site** — MkDocs | [Live](https://jumma786.github.io/seo-aeo-playbook/) | [`mkdocs.yml`](mkdocs.yml) |
| **Prompt library** — 13 prompts | Complete | [`prompts/`](prompts/) |
| **Checklists** — 6 checklists | Complete | [`checklists/`](checklists/) |
| **Templates** — 6 templates | Complete | [`templates/`](templates/) |
| **Case studies** — 2 walkthroughs | Complete | [`examples/case-studies/`](examples/case-studies/) |

> **A note on repository sprawl.** Early planning left a large number of empty directories and 0-byte files across the repo root, `docs/`, and `examples/`. Nothing references them and nothing depends on them. The table above is the accurate picture of what's real — treat everything else as scaffolding pending cleanup.

## The three books

They're written to be read in order, and each cross-references the others throughout.

**1. [SEO](docs/books/complete/seo/README.md)** — the foundation. How search engines crawl, render, index, and rank; search intent, keyword research, content optimization, entity SEO, internal linking, E-E-A-T, Core Web Vitals, and local SEO.

**2. [AEO](docs/books/complete/aeo/README.md)** — Answer Engine Optimization. How to become the cited source: passage-level citability, AI crawler access and `llms.txt`, and platform-specific tactics for ChatGPT, AI Overviews, Perplexity, Gemini, and Claude.

**3. [GEO](docs/books/complete/geo/README.md)** — Generative Engine Optimization, one layer deeper. Knowledge graphs, embeddings, vector search, and RAG — the retrieval machinery that explains *why* every AEO tactic works.

If you only read one thing first, read the SEO book's opening chapters. AEO without the crawling and indexing fundamentals is cargo-culting.

## The toolkit

The 24 modules in `scripts/` are plain, dependency-light Python with docstrings and doctests. They're exposed two ways.

### CLI

```bash
pip install -e .
seo-playbook --help
```

Covers schema generation and validation, sitemap/robots.txt/llms.txt generation, on-page and full-site audits, page-speed analysis, link checking, keyword clustering and cannibalization audits, entity extraction, internal link suggestions, GEO citability scoring, content briefs, FAQ and blog scaffolding, and governed local-SEO page templates.

Optional YAML config (`seo-playbook.yml`, auto-discovered) supplies `brand` / `domain` / `output_dir` defaults so you don't repeat yourself:

```bash
seo-playbook init --brand "Example Corp" --domain example.com
```

### HTTP API

```bash
pip install -e ".[api]"
uvicorn api.app:app --reload
```

Interactive Swagger UI at `http://127.0.0.1:8000/docs`; `/health` is a liveness probe.

> **Trust boundary — read before deploying.** The API ships **without authentication by design**. It's built for local and trusted-network use alongside the CLI, not as a public multi-tenant service. Two endpoints deliberately diverge from their CLI equivalents for this reason: the page generators return rendered content in the response rather than writing to a server-side path, and the book-docs endpoints accept content in the request body rather than reading a server-side directory. Both avoid handing a client arbitrary filesystem access. See [`api/routes.py`](api/routes.py) for details.

### Documentation site

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Repository structure

```text
seo-aeo-playbook/
├── docs/books/complete/{seo,aeo,geo}/   # the three books (38 chapters) — canonical location
├── docs/                                # MkDocs content (index, CLI reference)
├── scripts/                             # 24 modules implementing the toolkit
├── cli/                                 # click CLI exposing scripts/ as `seo-playbook`
├── api/                                 # FastAPI service exposing scripts/ over HTTP
├── tests/                               # 483-test pytest suite across scripts/cli/api
├── prompts/ checklists/ templates/      # content library
├── examples/case-studies/               # applied walkthroughs
├── mkdocs.yml                           # docs site config
└── pyproject.toml                       # packaging, entry point, dependency groups
```

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
```

The suite runs in a few seconds and requires no network access or API keys.

## Contributing

Contributions are welcome — issues and pull requests both.

1. Fork and create a feature branch.
2. Add tests for any new `scripts/`, `cli/`, or `api/` code. Match the established pattern: one `TestXxx` class per function, doctests in the module itself.
3. Run the full suite (`python -m pytest tests/ -q`) before opening the PR.
4. Open a pull request describing what changed and why.

For book content, follow the structure of an existing chapter: numbered sections, Best Practices, Common Mistakes, Checklist, Summary, Learning Outcomes, References.

## License

[MIT](LICENSE) © 2026 Jumma Mohammad

<div align="center">

**Built by [Jumma Mohammad](https://github.com/jumma786)** · [Read the docs](https://jumma786.github.io/seo-aeo-playbook/)

</div>
