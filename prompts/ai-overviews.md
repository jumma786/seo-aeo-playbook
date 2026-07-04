# Google AI Overviews Prompts

Platform-specific prompts for Google AI Overviews (formerly SGE). See [AEO Book, Chapter 4: Optimizing for Google AI Overviews](../docs/books/complete/aeo/chapter-04.md) and the general [AEO Prompts](aeo.md) for cross-platform citability work.

## 1. Question-Matched Heading Rewrite

```text
Here are headings from my page: {{list headings}}. The target query is "{{query}}".
Rewrite each heading to match natural question phrasing a person would actually type or
speak, while staying accurate to the section content below it — don't force a question
format where a heading is genuinely just a label (e.g. "Pricing").
```

**When to use:** Improving alignment between heading phrasing and the way AI Overviews tends to match content to questions.

## 2. Direct-Answer Opening Draft

```text
The target query is "{{query}}". Here is my section's supporting content: {{paste
content}}. Write a 1-2 sentence direct answer to open the section with, that could stand
alone as an AI Overview citation, followed by a smooth transition into the existing
supporting detail.
```

**When to use:** Retrofitting answer-first structure into existing content without a full rewrite.

## 3. Schema/Text Consistency Check

```text
Here is my page's visible text making a factual claim: {{paste text}}. Here is the
matching structured data field: {{paste schema field/value}}. Do these agree exactly?
Flag any discrepancy, however small (rounding, different units, an outdated number in one
but not the other).
```

**When to use:** AI Overviews and other answer engines weigh structured data as reinforcement of visible claims — a mismatch undermines both.

## 4. AI Overview Visibility Tracking Plan

```text
I want to track whether my content appears in Google AI Overviews for
{{N}} priority queries. I have access to: {{list tools, e.g. "Search Console, manual
search, a rank tracker"}}. Suggest a realistic, repeatable process to sample and log AI
Overview presence/absence over time given these tools.
```

**When to use:** Building the "AI visibility tracking" item from the [AEO Checklist](../checklists/aeo.md) into an actual repeatable process.

## 5. Featured Snippet to AI Overview Transition Check

```text
This content currently holds (or held) a Featured Snippet for "{{query}}": {{paste
snippet-winning passage}}. Is the phrasing/structure still well-suited to being lifted
into an AI Overview, or does it rely on visual/list formatting that wouldn't translate
to a generated summary?
```

**When to use:** Auditing legacy Featured-Snippet-optimized content as AI Overviews increasingly reshape that SERP real estate.
