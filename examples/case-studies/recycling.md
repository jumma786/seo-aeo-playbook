# Case Study: Recycling & Waste Management

> **This is an illustrative, composite example for demonstration purposes.** "GreenCycle Solutions" is a fictional company; it does not describe any real business's actual results. It walks through how the frameworks and tools in this repository would apply to a typical local/regional recycling business, not a documented outcome.

## Business Profile

GreenCycle Solutions operates recycling drop-off and collection services across several municipalities, serving both residential customers (curbside pickup) and commercial clients (bulk material recycling, dumpster rental). Their business is inherently local and multi-location — success depends on ranking for both "near me" residential queries and commercial B2B service queries, in every municipality served.

## Starting Situation

- One generic "Service Areas" page listing city names with no dedicated content per city
- Inconsistent NAP (Name, Address, Phone) across Google Business Profile, the website, and directory listings
- No structured data distinguishing which locations were staffed drop-off centers versus which areas were served without a physical presence
- No FAQ content addressing common questions (what materials are accepted, pricing, pickup scheduling)

## Applying the SEO Book

**Local SEO ([Chapter 19](../../docs/books/complete/seo/chapter-19.md)):** The core issue was conflating two different business models on one generic page — staffed drop-off centers (which have a real public address) and residential/commercial pickup service areas (which don't). Split into two governed page types:

- **Drop-off center locations** — one page per staffed facility, each with full NAP, hours, and `LocalBusiness` schema, generated via `seo-playbook location-pages` (which enforces unique content and NAP completeness as quality gates).
- **Service-area pages** — one page per municipality served by pickup-only service, generated via `seo-playbook service-pages`, which structurally has no street-address field — critical here, since falsely implying a staffed office in every served municipality would violate Google's guidelines and risk suspension.

**NAP consistency:** Audited and corrected NAP across all citations, using the canonical NAP from each drop-off center page as the source of truth. See the [Local SEO Checklist](../../checklists/local-seo.md).

**FAQ content ([Chapter 9, Section 20](../../docs/books/complete/seo/chapter-09.md)):** Built out FAQ sections per service area (accepted materials, pricing, scheduling) using the [FAQ Template](../../templates/faq-template.md) and `seo-playbook faq`, which validates that each answer is self-contained and citable rather than a vague fragment.

## Applying the AEO/GEO Books

Residential customers increasingly ask AI assistants location-specific questions directly ("does GreenCycle recycle electronics in [city]," "how much is bulk pickup near me"). Because service-area pages avoid any physical-address claim, and each FAQ answer names the service and area explicitly rather than relying on "we" with no antecedent, these pages are structured to be citable by an AI answer engine without accidentally implying an office that doesn't exist in that city.

## Illustrative Outcome

In a scenario like this, the expected qualitative impact is: residents and commercial clients finding a genuinely relevant page for their specific municipality instead of a generic list, consistent citation data reducing map-pack confusion between similarly-named nearby cities, and structurally correct schema avoiding the guidelines risk that comes from a service-area business overstating its physical footprint. This case study does not report specific traffic, ranking, or lead-volume numbers, since none were measured for a fictional example.

## Tools referenced in this case study

`seo-playbook location-pages`, `service-pages`, `faq`, `schema validate` — see the [CLI Reference](../../docs/cli-reference.md) and the [Local SEO Checklist](../../checklists/local-seo.md).
