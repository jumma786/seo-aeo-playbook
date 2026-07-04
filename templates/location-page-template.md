# Location Page Template

A copy-paste starting point for a single storefront/multi-location page. For governed, quality-gated generation at scale (rejecting thin or duplicated content automatically), use `seo-playbook location-pages` — see [`scripts/location_page_generator.py`](../scripts/location_page_generator.py) and the [Local SEO Checklist](../checklists/local-seo.md).

---

```markdown
# [Business Name] — [City], [State]

[150-200 words of UNIQUE content for this specific location — not boilerplate
that could apply to any location. Include at least two specific, local details:
a landmark or neighborhood served, how long this location has operated, staff
unique to this location, or a service unique to this location. This is the
single most important part of the page — thin or duplicated location content
is explicitly flagged as a Google guidelines risk (see SEO Book, Chapter 19,
Section 11).]

## Location Details

**Address:** [Street Address], [City], [State] [ZIP]
**Phone:** [Phone Number]
**Hours:**

- Monday: [hours]
- Tuesday: [hours]
- Wednesday: [hours]
- Thursday: [hours]
- Friday: [hours]
- Saturday: [hours]
- Sunday: [hours]

## Staff at This Location

[Names/roles of staff specific to this location, if applicable — reinforces
E-E-A-T and page uniqueness.]

## Services at This Location

[Any services specific to or emphasized at this location, if they differ from
other locations.]

## Local Testimonials

[Genuine reviews/testimonials specific to this location, not generic
company-wide quotes reused across every page.]

<!-- Embed a map here -->
<!-- Generate matching LocalBusiness schema: seo-playbook location-pages specs.json output_dir/ -->
```

---

## Quality gates (enforced automatically by `seo-playbook location-pages`)

- [ ] Unique content is at least ~50 words and genuinely distinct from every sibling location page
- [ ] Full NAP (Name, Address, Phone) present and accurate
- [ ] `LocalBusiness` schema scoped to this specific location, not shared/generic

**Note:** this template is for a business with a real, public physical address. If you're a service-area business (no public office in every area you serve), use the [Service Page Template](service-page-template.md) instead — it deliberately has no address field at all.
