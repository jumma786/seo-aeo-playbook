# FAQ Section Template

A copy-paste starting point for an FAQ section, following the citability criteria `scripts/faq_generator.py` validates automatically (question phrasing, answer length, self-containedness). See [SEO Book, Chapter 9, Section 20](../docs/books/complete/seo/chapter-09.md) and [AEO Book, Chapter 7](../docs/books/complete/aeo/chapter-07.md).

---

```markdown
## Frequently Asked Questions

### What is [term/product]?

[15-60 word answer. Name the subject explicitly in the first few words — don't
open with "It is..." Example: "[Term] is a [category] that [does X], used
for [purpose]."]

### How does [term/product] work?

[15-60 word answer, stated as a complete claim, not a fragment.]

### How much does [product/service] cost?

[15-60 word answer with a specific, checkable number or range where possible —
specific facts are more citable than vague statements like "it depends."]

### Is [product/service] right for [use case]?

[15-60 word answer giving a direct yes/no/it-depends-because answer, not just
a restatement of the question.]

### What's the difference between [X] and [Y]?

[15-60 word answer stating the key distinguishing factor directly.]
```

---

## Rules this template follows (and `seo-playbook faq` validates)

- [ ] Each question is a real question a user would ask, ending in `?`, starting with a recognizable question word (What/How/Is/Does/etc.)
- [ ] Each answer is 15-60 words — long enough to be a complete, useful claim; short enough to be a clean citation/snippet
- [ ] No answer opens with a dangling pronoun ("It...", "This...") — name the subject
- [ ] Questions come from real user language (support tickets, search queries, People Also Ask), not invented to hit a keyword

## Generating the matching schema

Once written, generate both the rendered Markdown and matching `FAQPage` JSON-LD together, so they never drift apart:

```bash
seo-playbook faq faq.json --output faq-section.md
```

where `faq.json` is `[{"question": "...", "answer": "..."}, ...]`.
