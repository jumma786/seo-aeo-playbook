## What does this change, and why?

<!-- If you're removing or correcting something, say what was wrong with it. -->

## Checks

- [ ] `python -m pytest tests/ -q` passes (the full suite, not just the files I touched)
- [ ] `mkdocs build --strict` exits 0
- [ ] Doctests run, if I changed a script that has them

## If this adds or changes a tool

- [ ] Tests added in `tests/test_<name>.py`
- [ ] Wired into the CLI (and the API, if it fits) with tests
- [ ] The docstring is honest about what the tool does *not* do
- [ ] If it scores or grades anything: I tested it against inputs where I know the right answer

## If this touches the books

- [ ] Every statistic cites a source a reader can follow
- [ ] Every reference has a URL, and I checked each one resolves
- [ ] Claims are marked as measured or inferred, not blurred together
- [ ] Relative links verified by resolution, not by counting `../` by eye

<!-- On sourcing: an unsourced figure is not a small problem here. The books previously
     carried an invented statistic and 38 chapters of unlinked references, and both had
     to be ripped out. If you can't source a number, write the claim qualitatively. -->
