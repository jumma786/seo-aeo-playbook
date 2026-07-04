# Service-Area Page Template

A copy-paste starting point for a service-area business page (plumber, cleaner, contractor — any business serving an area without necessarily having a public office there). For governed, quality-gated generation at scale, use `seo-playbook service-pages` — see [`scripts/service_page_generator.py`](../scripts/service_page_generator.py) and the [Local SEO Checklist](../checklists/local-seo.md).

---

```markdown
# [Service Name] in [Area Served] | [Business Name]

[150-200 words of UNIQUE content for this specific service area — not
boilerplate reused across every area page with only the city name swapped.
Include specific, local detail (typical response time in this area, a
local landmark/neighborhood, a locally-relevant example) and describe the
service itself concretely. Do NOT state or imply a physical office/address
in this area if one doesn't exist — see the note below.]

## Service Details

**Service:** [Service Name]
**Area served:** [City/Region, State]
**Phone:** [Phone Number]

## Why Choose Us for [Service] in [Area]

[Specific differentiators — licensing, experience, guarantees, response time.]

## Frequently Asked Questions

### How quickly can you respond in [area]?

[15-60 word answer with a specific, checkable claim.]

### Do you serve all of [area], including [specific neighborhood]?

[15-60 word answer.]

<!-- Generate matching LocalBusiness schema (using areaServed, NOT a street
     address) via: seo-playbook service-pages specs.json output_dir/ -->
```

---

## Critical rule: no physical address, ever

Service-area businesses must never publish a street address or claim a physical presence in an area they don't actually have an office in — doing so violates Google's guidelines and risks account suspension. `scripts/service_page_generator.py`'s `ServiceAreaPageSpec` structurally has no street-address field at all, and its generated schema uses `areaServed` instead of `address` — use it (or this template, carefully) rather than adapting the [Location Page Template](location-page-template.md), which assumes a real public address.

## Quality gates (enforced automatically by `seo-playbook service-pages`)

- [ ] Unique content is at least ~50 words and genuinely distinct from every sibling service-area page
- [ ] No street address anywhere on the page
- [ ] `business_name`, `service_name`, `area_served`, and `telephone` all present
