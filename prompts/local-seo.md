# Local SEO Prompts

For Google Business Profile, location pages, and review management. See [SEO Book, Chapter 19: Local SEO](../docs/books/complete/seo/chapter-19.md) and the [Local SEO Checklist](../checklists/local-seo.md).

## 1. Location Page Unique Content Draft

```
Write 150-200 words of unique, substantive content for the {{city, state}} location page
of {{business name}}, a {{business type}}. Include at least two specific, local details
(a landmark, a neighborhood served, how long this location has operated, a specific
service unique to this location) — not boilerplate that could apply to any location.
Do not include the street address or phone number; those are handled separately.
```

**When to use:** Feed the output into `unique_content` for `seo-playbook location-pages` (storefronts) or `service-pages` (service-area businesses) — both reject content under ~50 words or duplicated across sibling locations.

## 2. GBP Description Draft

```
Write a Google Business Profile description (under 750 characters) for {{business name}},
a {{business type}} in {{city}}. Cover what the business does, its unique differentiator,
and primary services, in plain factual language — no keyword stuffing, no superlatives
without backing ("best in town").
```

**When to use:** Setting up or refreshing a Google Business Profile.

## 3. Review Response Templates

```
Draft three review response templates for {{business type}}: one for a 5-star review
mentioning {{example detail}}, one for a 3-star review citing {{example complaint}}, and
one for a 1-star review alleging {{example serious complaint}}. Keep responses genuine and
specific to the review content, not generic "thank you for your feedback."
```

**When to use:** Building a consistent, non-generic review response process.

## 4. Citation Consistency Audit Prompt

```
Here is my NAP (Name, Address, Phone) as it should appear: {{canonical NAP}}. Here is how
it currently appears across these listings: {{paste variations found}}. Flag every
inconsistency, however minor (abbreviations, suite number formatting, old phone numbers).
```

**When to use:** Periodic citation consistency audits.

## 5. Service-Area Messaging Check

```
My business serves {{list of cities/areas}} without a public office in most of them. Review
this page draft: {{paste draft}}. Flag any language that implies a physical presence or
office in an area we don't actually have one in — this is a Google guidelines violation
for service-area businesses.
```

**When to use:** Before publishing any service-area page — pairs with `seo-playbook service-pages`, which structurally can't accept a street address at all.
