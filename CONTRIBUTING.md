# Contributing

Thanks for considering a contribution. This repository holds three books, a Python toolkit (`scripts/`), a CLI wrapping it (`cli/`), and a FastAPI service exposing the same functions (`api/`). The docs site is built from `docs/` with MkDocs.

## Getting set up

```bash
git clone https://github.com/jumma786/seo-aeo-playbook.git
cd seo-aeo-playbook
python -m pip install -e ".[api,docs]"
python -m pytest tests/ -q          # should report all tests passing
```

Python 3.10 or newer is required.

## Before you open a pull request

Run all three. CI runs the first two; the third catches broken chapter links.

```bash
python -m pytest tests/ -q          # full suite, not just the file you touched
mkdocs build --strict               # must exit 0
python -m doctest scripts/<file>.py # if you changed a script with doctests
```

## The evidence rule

This project makes factual claims about how search and answer engines behave, and those claims need to be checkable.

- **Every statistic must cite a source the reader can follow.** If you cannot source a figure, write the claim qualitatively instead. A fabricated number is worse than a vague sentence: a vague sentence merely fails to persuade, a wrong one gets quoted.
- **Link references, don't just name them.** A reference without a URL cannot be verified, and titles written from memory are often wrong.
- **Verify links resolve before submitting.** Not "I'm fairly sure that page exists."
- **Separate measured from inferred.** If something is reasoning about how retrieval works rather than a tested result, say so.

This is not boilerplate — the books previously contained an invented statistic and 38 chapters of unlinked references, both of which had to be removed. See AEO Chapter 7, Section 5a for the standard we hold claims to.

## Adding a script

Scripts follow a consistent pattern. If you add one:

1. **Ground it in the books.** Grep `docs/books/` for the topic first; behaviour should implement something the books document rather than an unrelated design.
2. **Match the existing style** — dataclasses, type hints, module docstring explaining what the tool does *and what it does not do*.
3. **Be honest about limitations in the docstring.** `scripts/entity_extractor.py` states plainly that it is a heuristic and points to spaCy for production use. That is the standard.
4. **Write a doctest and actually run it.** Don't hand-trace the expected output.
5. **Add tests** in `tests/test_<name>.py`, one `TestXxx` class per function.
6. **Wire it into the CLI** (`cli/commands.py`) with tests in `tests/test_cli.py`, and into the API if it fits.
7. **Run the full suite** before committing.

Don't ship a tool that scores or grades something unless you have tested it against inputs where you know the right answer. A tool that gives confidently wrong advice is worse than no tool.

## Book chapters

Chapters live in `docs/books/complete/{seo,aeo,geo}/chapter-NN.md`. Other book-shaped directories are historical and unused.

Relative link depth catches people out: from a chapter, sibling books are `../aeo/...` (one level up), but repo-root directories are `../../../../prompts/...` (four levels up). Verify with a resolution check rather than counting `../` by eye.

## Commit messages

Explain why the change is correct, not just what changed. If you removed something, say what was wrong with it.

## Reporting problems

Found an unsourced claim, a broken link, or a tool that gives bad advice? That is a bug — please open an issue. Corrections to the books are as welcome as code.
