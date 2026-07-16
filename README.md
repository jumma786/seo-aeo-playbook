<div align="center">

# SEO / AEO / GEO Playbook

**An open-source reference for search visibility — and a tested Python toolkit that implements it.**

Rank on Google. Get cited by ChatGPT, AI Overviews, Gemini, Claude, and Perplexity.

[![Docs](https://img.shields.io/badge/docs-live-2ea44f)](https://jumma786.github.io/seo-aeo-playbook/)
[![Tests](https://github.com/jumma786/seo-aeo-playbook/actions/workflows/tests.yml/badge.svg)](https://github.com/jumma786/seo-aeo-playbook/actions/workflows/tests.yml)
[![Markdown](https://github.com/jumma786/seo-aeo-playbook/actions/workflows/markdown.yml/badge.svg)](https://github.com/jumma786/seo-aeo-playbook/actions/workflows/markdown.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[**Read the docs**](https://jumma786.github.io/seo-aeo-playbook/) · [**CLI reference**](docs/cli-reference.md) · [**Start with the SEO Book**](docs/books/complete/seo/README.md) · [**Contributing**](CONTRIBUTING.md)

</div>

---

## Why this exists

Ranking on Google is no longer the whole job. The same content now has to be **retrievable, citable, and structurally unambiguous** to answer engines that synthesise a response instead of returning ten blue links.

Most SEO resources give you prose you can't execute, or tools that don't explain themselves. This repository is deliberately both halves:

- **38 chapters** across three books explaining the mechanics — not tips, but how crawling, indexing, ranking, retrieval, and citation actually work.
- **A tested Python toolkit** — 21 CLI commands and a 25-endpoint HTTP API — implementing the practices those chapters describe.

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

A few more of the 21 commands:

```bash
# Scaffold a project config that other commands read defaults from
seo-playbook init --brand "Example Corp" --domain example.com

# Generate validated Schema.org JSON-LD
seo-playbook schema article --headline "..." --author "..." --date-published 2026-01-15

# Group keywords into topic clusters, then find cannibalisation
seo-playbook cluster keywords.txt
seo-playbook keyword-map audit mapping.json

# Generate an llms.txt from a spec, then audit robots.txt for AI crawler access
seo-playbook llms generate llms-spec.json
seo-playbook llms audit-crawlers robots.txt

# SEO + schema + performance across many URLs, one fetch per page
seo-playbook site-audit urls.txt
```

See the [CLI reference](docs/cli-reference.md) for all 21 commands and their options.

## What's inside

| Component | Scope | Location |
|---|---|---|
| **SEO Book** | 20 chapters | [`docs/books/complete/seo/`](docs/books/complete/seo/README.md) |
| **AEO Book** | 10 chapters | [`docs/books/complete/aeo/`](docs/books/complete/aeo/README.md) |
| **GEO Book** | 8 chapters | [`docs/books/complete/geo/`](docs/books/complete/geo/README.md) |
| **Toolkit** | 23 modules | [`scripts/`](scripts/) |
| **CLI** | 21 commands | [`cli/`](cli/) |
| **HTTP API** | 25 endpoints | [`api/`](api/) |
| **Test suite** | 459 tests, 27 files | [`tests/`](tests/) |
| **Documentation site** | MkDocs — [live](https://jumma786.github.io/seo-aeo-playbook/) | [`mkdocs.yml`](mkdocs.yml) |
| **Prompt library** | 13 prompts | [`prompts/`](prompts/) |
| **Checklists** | 6 checklists | [`checklists/`](checklists/) |
| **Templates** | 6 templates | [`templates/`](templates/) |
| **Case studies** | 2 walkthroughs (illustrative, not real clients) | [`examples/case-studies/`](examples/case-studies/) |

## The three books

Written to be read in order, and cross-referenced throughout.

**1. [SEO](docs/books/complete/seo/README.md)** — the foundation. How search engines crawl, render, index, and rank; search intent, keyword research, content optimisation, entity SEO, internal linking, E-E-A-T, Core Web Vitals, and local SEO.

**2. [AEO](docs/books/complete/aeo/README.md)** — Answer Engine Optimization. How to become the cited source: passage-level citability, AI crawler access and `llms.txt`, and platform-specific tactics for ChatGPT, AI Overviews, Perplexity, Gemini, and Claude.

**3. [GEO](docs/books/complete/geo/README.md)** — Generative Engine Optimization, one layer deeper. Knowledge graphs, embeddings, vector search, and RAG — the retrieval machinery that explains *why* every AEO tactic works.

If you only read one thing first, read the SEO book's opening chapters. AEO without the crawling and indexing fundamentals is cargo-culting.

## How this is verified

Search advice is unusually prone to confident nonsense, so the standards here are mechanical rather than aspirational:

- **Every reference resolves.** All 91 links across the 38 chapters were fetched and checked against the live page title — not written from memory. That process found that *"Google Search Central: E-E-A-T Guidelines"*, widely cited across the industry, is not a real document.
- **Claims are marked measured or inferred.** Where research has actually tested something, the chapter says so and cites it. Where it's reasoning from how retrieval works, it says that instead. See [AEO Chapter 7 §5a](docs/books/complete/aeo/chapter-07.md).
- **Statistics cite a source, or don't appear.** An invented figure was found in these books and removed. The rule that replaced it is in [CONTRIBUTING.md](CONTRIBUTING.md): if you can't source a number, write the claim qualitatively.
- **Tools state their limits.** [`entity_extractor.py`](scripts/entity_extractor.py) tells you in its own docstring to use spaCy for production work.
- **A tool that failed its own test was deleted.** A citability scorer shipped here until it was tested against known inputs: a content-free paragraph scored 100/100, a genuinely useful sentence scored 0/100. It was anti-correlated with what it claimed to measure, so it was removed — script, tests, CLI command, and endpoint. A tool giving confident wrong advice is worse than no tool.

## The toolkit

The 23 modules in `scripts/` are plain, dependency-light Python with docstrings and doctests, exposed two ways.

### CLI

```bash
pip install -e .
seo-playbook --help
```

Covers schema generation and validation, sitemap / robots.txt / llms.txt generation, on-page and full-site audits, page-speed analysis, link checking, keyword clustering and cannibalisation audits, entity extraction, internal link suggestions, content briefs, FAQ and blog scaffolding, and governed local-SEO page templates.

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

> **Trust boundary — read before deploying.** The API ships **without authentication by design**. It's built for local and trusted-network use alongside the CLI, not as a public multi-tenant service. Several tools fetch URLs you supply, so exposing them to untrusted callers creates an SSRF vector. Two endpoints deliberately diverge from their CLI equivalents for related reasons: the page generators return rendered content in the response rather than writing to a server-side path, and the book-docs endpoints accept content in the request body rather than reading a server-side directory. Both avoid handing a client arbitrary filesystem access. See [SECURITY.md](SECURITY.md).

### Documentation site

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Repository structure

```text
seo-aeo-playbook/
├── docs/books/complete/{seo,aeo,geo}/   # the three books (38 chapters)
├── docs/                                # MkDocs content (index, CLI reference)
├── scripts/                             # 23 modules implementing the toolkit
├── cli/                                 # click CLI exposing scripts/ as `seo-playbook`
├── api/                                 # FastAPI service exposing scripts/ over HTTP
├── tests/                               # 459-test pytest suite across scripts/cli/api
├── prompts/ checklists/ templates/      # content library
├── examples/case-studies/               # applied walkthroughs
├── mkdocs.yml                           # docs site config
└── pyproject.toml                       # packaging, entry point, dependency groups
```

## Development

```bash
pip install -e ".[api,dev]"
python -m pytest tests/ -q
```

The suite runs in seconds and needs no network access or API keys. CI runs it on Python 3.10 and 3.12.

## Contributing

Contributions are welcome — issues and pull requests both. Corrections to the books count: an unsourced claim or a dead reference link is a bug, and reporting one is as useful as a patch.

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for setup, the pattern for adding a script, and the evidence rule for book content.

## License

[MIT](LICENSE) © 2026 Jumma Mohammad

<div align="center">

**Built by [Jumma Mohammad](https://github.com/jumma786)** · [Read the docs](https://jumma786.github.io/seo-aeo-playbook/)

</div>
