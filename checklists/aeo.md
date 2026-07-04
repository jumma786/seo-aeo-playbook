# AEO (Answer Engine Optimization) Checklist

Synthesized from the per-chapter checklists across the [AEO Book](../docs/books/complete/aeo/README.md) (10 chapters). Covers the practices shared across ChatGPT Search, Google AI Overviews, Perplexity, Gemini, and Claude, plus platform-specific items.

## Foundation

- [ ] Technical SEO foundation confirmed solid first — crawlable, indexable, fast (AEO builds on SEO, not around it)
- [ ] AI crawler access explicitly configured in `robots.txt`, not left to default — `seo-playbook llms audit-crawlers` audits this against the known crawler directory (GPTBot, OAI-SearchBot, ChatGPT-User, Google-Extended, PerplexityBot, ClaudeBot, Bingbot, CCBot)
- [ ] Key content verified to render without requiring client-side JavaScript
- [ ] `llms.txt` published at site root with curated, current links — `seo-playbook llms generate`
- [ ] `llms-full.txt` published if the site is documentation-heavy

## Citability (applies to every answer engine)

- [ ] Each key section/passage is self-contained — understandable without reading the rest of the page (no opening with "it"/"this" referring outside the passage)
- [ ] Each section opens with a direct answer or claim before supporting detail
- [ ] Facts are specific and checkable, not vague — `seo-playbook geo-score` flags passages missing a specific/checkable fact
- [ ] Clear structural signals used throughout: descriptive subheadings, lists, short paragraphs, explicit labels ("Definition:", "Step 1:")
- [ ] Authorship and publication/modification dates visible and reinforced with `Article` schema

## Platform-Specific

- [ ] **ChatGPT Search:** `OAI-SearchBot`/`ChatGPT-User` explicitly allowed; `GPTBot` (training) opt-out set as a deliberate, separate decision
- [ ] **Google AI Overviews:** headings phrased to match natural question wording; structured data reinforces the same facts stated in visible text
- [ ] **Perplexity:** `PerplexityBot` explicitly allowed; time-sensitive content kept current
- [ ] **Gemini & Claude:** `Google-Extended` and `ClaudeBot` access policies each set deliberately, independent of standard `Googlebot`/organic crawling

## FAQ & Conversational Content

- [ ] Real user prompts collected from support logs, forums, or direct testing — not guessed
- [ ] FAQ headers phrased as natural, full questions — `seo-playbook faq` validates question phrasing and answer length/self-containedness against exactly these criteria
- [ ] Content mapped to definition / comparison / how-to / recommendation / troubleshooting query patterns

## Measurement

- [ ] A representative prompt panel defined and sampled on a recurring schedule
- [ ] Server logs analyzed for AI crawler activity
- [ ] GA4 configured to correctly classify AI platform referral traffic
- [ ] AI visibility/citation-rate tracking connected to downstream business outcomes, not tracked in isolation

## References

All 10 chapters of the [AEO Book](../docs/books/complete/aeo/README.md), especially:

- [Chapter 7: AI Citations & Passage-Level Citability](../docs/books/complete/aeo/chapter-07.md)
- [Chapter 8: llms.txt & AI Crawler Accessibility](../docs/books/complete/aeo/chapter-08.md)
- [Chapter 10: AEO Measurement & Analytics](../docs/books/complete/aeo/chapter-10.md)
