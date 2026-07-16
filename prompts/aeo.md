# AEO (Answer Engine Optimization) Prompts

General prompts spanning multiple answer engines. For platform-specific prompts, see [AI Overviews Prompts](ai-overviews.md). See the [AEO Checklist](../checklists/aeo.md) and the [AEO Book](../docs/books/complete/aeo/README.md).

## 1. Passage Self-Containment Rewrite

```text
Here is a paragraph flagged as not self-contained: {{paste paragraph, e.g. one starting
with "It provides..."}}. Rewrite it to name its subject explicitly in the first sentence,
so it reads as a complete, unambiguous claim if quoted alone, out of context.
```

**When to use:** Fixing a passage that opens with "It"/"This"/"They" referring to a subject named somewhere else, so it can't stand alone if quoted.

## 2. Answer-First Restructure

```text
Here is a section that builds up to its main point at the end: {{paste section}}. Rewrite
it to lead with the direct answer or claim in the first sentence, then follow with
supporting detail — without losing any of the original substance.
```

**When to use:** Restructuring content for passage-level retrieval, which favors answer-first writing over narrative build-up.

## 3. llms.txt Content Curation

```text
Here is my site's navigation/sitemap: {{paste structure}}. Select the 8-12 most
important pages an AI agent should be pointed to first, grouped into logical sections
(Documentation, Guides, Reference, Optional). For each, write a one-line description.
```

**When to use:** Drafting the input for `seo-playbook llms generate`.

## 4. Structural Label Insertion

```text
Here is a section of instructional content: {{paste content}}. Add explicit structural
labels ("Definition:", "Requirement:", "Step 1:", "Step 2:") where they'd help both human
skimmers and extraction systems identify what type of information each part contains,
without changing the actual instructions.
```

**When to use:** Making instructional content's structure explicit, so an extraction system can tell a definition from a step from a caveat.

## 5. AI Crawler Policy Decision Draft

```text
My stance on AI training data use is {{describe: opt-in / opt-out / undecided}}, and I
{{do/do not}} want to appear in AI-powered search results. Based on this, what should my
robots.txt policy be for GPTBot, OAI-SearchBot, ChatGPT-User, Google-Extended, ClaudeBot,
and PerplexityBot specifically (these are separate decisions, not one on/off switch)?
```

**When to use:** Making a deliberate, documented AI crawler policy rather than leaving it to defaults — validate the resulting robots.txt with `seo-playbook llms audit-crawlers`.
