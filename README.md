# 🚀 SEO / AEO / GEO Playbook

<div align="center">

![SEO](https://img.shields.io/badge/SEO-38%20chapters-blue?style=for-the-badge)
![AEO](https://img.shields.io/badge/AEO-Answer%20Engine-green?style=for-the-badge)
![GEO](https://img.shields.io/badge/GEO-Generative%20Engine-orange?style=for-the-badge)
![License](https://img.shields.io/github/license/jumma786/seo-aeo-playbook?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/jumma786/seo-aeo-playbook?style=for-the-badge)
![Forks](https://img.shields.io/github/forks/jumma786/seo-aeo-playbook?style=for-the-badge)

## 📈 A Complete, Practitioner-Grade Guide to SEO, AEO & GEO — Plus a CLI + API Toolkit That Implements It

*From crawling fundamentals to AI-generated answers: rank on Google and get cited by ChatGPT, Google AI Overviews, Gemini, Claude, and Perplexity.*

⭐ **Star this repository if you find it useful!**

</div>

---

# 📖 About

Search is changing. Ranking on Google is no longer enough — content also needs to be retrievable, citable, and structured in a way AI answer engines can use.

This repository is two things at once:

1. **Three complete books** (38 chapters) covering traditional SEO, Answer Engine Optimization (AEO), and Generative Engine Optimization (GEO) — the technology stack underneath AI search.
2. **A working Python toolkit** — a CLI and a FastAPI service — that implements the practices those books describe: schema generation and validation, sitemap/robots.txt/llms.txt generation, keyword clustering and cannibalization audits, entity extraction, internal link suggestions, page-speed and full-site audits, content briefs, FAQ generation, and governed local-SEO page templates.

Whether you're reading to learn or scripting against the CLI/API to automate your own SEO workflow, this project is built to be actually used, not just read.

---

# ✨ What's Actually Here

| Component | Status | Where |
|---|---|---|
| **SEO Book** (20 chapters) | ✅ Complete | [`docs/books/complete/seo/`](docs/books/complete/seo/README.md) |
| **AEO Book** (10 chapters) | ✅ Complete | [`docs/books/complete/aeo/`](docs/books/complete/aeo/README.md) |
| **GEO Book** (8 chapters) | ✅ Complete | [`docs/books/complete/geo/`](docs/books/complete/geo/README.md) |
| **CLI** (`seo-playbook`, 24 commands) | ✅ Complete, fully tested | [`cli/`](cli/) |
| **Python toolkit** (24 scripts) | ✅ Complete, fully tested | [`scripts/`](scripts/) |
| **FastAPI service** (~25 endpoints) | ✅ Complete, fully tested | [`api/`](api/) |
| **Documentation site** (MkDocs) | ✅ Configured, builds clean | [`mkdocs.yml`](mkdocs.yml), [`docs/`](docs/) |
| Prompt library / checklists / templates / case studies | 🚧 Scaffolded, not yet populated | `prompts/`, `checklists/`, `templates/`, `examples/` |

The repository also contains a large amount of early scaffolding (empty directories and 0-byte files under the repo root and `docs/`) from initial planning that was never built out. It's harmless — nothing references it — but don't take its presence as a signal of what's actually implemented; the table above is the accurate picture.

---

# 🧰 Using the Toolkit

Install the package and its CLI entry point:

```bash
pip install -e .
seo-playbook --help
```

Every practice documented in the books has a corresponding command — see the [CLI Reference](docs/cli-reference.md) for the full list. A few examples:

```bash
seo-playbook init --brand "Example Corp" --domain example.com   # scaffold a project config
seo-playbook audit https://example.com                          # on-page SEO audit
seo-playbook schema article --headline "..." --author "..." --date-published 2026-01-15
seo-playbook cluster keywords.txt                                # lexical keyword clustering
seo-playbook site-audit urls.txt                                 # SEO + schema + page-speed, one pass
```

## Run the API

```bash
pip install -e ".[api]"
uvicorn api.app:app --reload
```

Then open `http://127.0.0.1:8000/docs` for interactive Swagger UI over every endpoint. The API mirrors the CLI's capabilities; see [`api/routes.py`](api/routes.py) for the full endpoint list and its documented trust-boundary assumptions (no auth — built for local/trusted use, not a public multi-tenant service).

## Run the documentation site locally

```bash
pip install -e ".[docs]"
mkdocs serve
```

---

# 📂 Repository Structure

```text
seo-aeo-playbook/
├── docs/books/complete/{seo,aeo,geo}/   # the three books (38 chapters), canonical location
├── docs/                                 # MkDocs site content (index, CLI reference, book pages)
├── scripts/                              # 24 standalone Python modules implementing the toolkit
├── cli/                                  # click-based CLI wiring scripts/ up as `seo-playbook`
├── api/                                  # FastAPI service wiring scripts/ up over HTTP
├── tests/                                # full pytest suite (400+ tests) for scripts/cli/api
├── mkdocs.yml                            # documentation site configuration
├── pyproject.toml                        # packaging, CLI entry point, optional dependency groups
└── prompts/ checklists/ templates/ examples/case-studies/   # content library
```

---

# 🛣 Reading Order

The three books build on each other:

1. **SEO** establishes the foundation — crawling, indexing, ranking, on-page and technical SEO.
2. **AEO** extends that into AI answer engines — platform-specific tactics for ChatGPT, Google AI Overviews, Perplexity, Gemini, and Claude.
3. **GEO** goes one layer deeper into the retrieval technology (knowledge graphs, embeddings, vector search, RAG) that makes every AEO tactic work mechanically.

Each book cross-references the others throughout its chapters.

---

# 🎯 Who Is This For?

SEO professionals, marketing agencies, freelancers, developers, startup founders, business owners, students, bloggers, content writers, and digital marketers — anyone who wants both the conceptual grounding and working tools for modern search visibility.

---

# 🤝 Contributing

Contributions are welcome. To propose a change:

1. Fork the repository
2. Create a feature branch
3. Add tests for any new `scripts/`, `cli/`, or `api/` code (see existing modules for the established pattern)
4. Open a Pull Request

---

# 📜 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

## 🚀 Learn SEO. Master AI Search. Automate the Practice

**Made with ❤️ by [Jumma Mohammad](https://github.com/jumma786)**

</div>
