# Content Gap Analysis Prompts

Finding topics and subtopics your site should cover but doesn't. For the mechanical, entity-level version of this, see `seo-playbook entities <content> --compare <competitor-content>`.

## 1. Topic Cluster Gap Map

```text
My site's content on {{broad topic}} currently covers: {{list your existing pages/titles}}.
A comprehensive treatment of this topic typically also covers subtopics like the ones a
pillar page in this space would need. Based on general knowledge of {{broad topic}}, list
subtopics a thorough resource would cover that I'm missing, grouped by whether they're
foundational, intermediate, or advanced.
```

**When to use:** Planning a pillar-and-cluster content architecture (see the `seo-cluster` skill for SERP-overlap-based clustering, a more rigorous version of this).

## 2. Question Gap from Real Users

```text
Here are support tickets / forum posts / community questions about {{topic}}:
{{paste real user questions}}. Which of these questions does my current content
(listed here: {{your pages}}) NOT answer? Prioritize by how frequently the question
seems to come up.
```

**When to use:** Grounding content gaps in real user language rather than guessed keywords — feed answered gaps into `seo-playbook faq`.

## 3. Entity Gap Narrative

```text
Here is the list of entities my content mentions: {{output of `seo-playbook entities`}}.
Here is the list from a competitor's content on the same topic: {{their entity list}}.
For each entity present in theirs but not mine, explain in one sentence why a
comprehensive piece on this topic would likely need to mention it.
```

**When to use:** Turning the raw output of `seo-playbook entities --compare` into an actionable content brief.

## 4. Format Gap Check

```text
My content on {{topic}} is currently: {{describe format, e.g. "a single long-form blog
post"}}. Competing/ranking content for this topic often uses formats like comparison
tables, calculators, checklists, or video. Which format(s) is my content missing that
would materially help users complete their task?
```

**When to use:** When a page has solid coverage but still underperforms — the gap may be structural, not topical.
