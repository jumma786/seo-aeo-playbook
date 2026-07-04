# Local SEO Checklist

For brick-and-mortar, service-area, and multi-location businesses. See [SEO Book, Chapter 19: Local SEO](../docs/books/complete/seo/chapter-19.md) for the full discussion.

## Google Business Profile & NAP

- [ ] Google Business Profile fully optimized and verified
- [ ] NAP (Name, Address, Phone) consistent across the website, GBP, and top citation sources
- [ ] Local citation audit completed and duplicate/outdated listings merged or removed

## Location & Service-Area Pages

- [ ] Unique, substantive location page per physical location — no thin, templated duplicates. `seo-playbook location-pages` enforces this as a hard quality gate (rejects unique content under ~50 words, and rejects content duplicated across sibling locations) before it will render a page
- [ ] `LocalBusiness` schema implemented per location, scoped with the location's own NAP
- [ ] **Service-area businesses only:** no street address published or claimed anywhere for areas served without a physical office — `seo-playbook service-pages` structurally enforces this (its spec has no street-address field at all; schema uses `areaServed` instead of `address`), since falsely implying a physical presence violates Google's guidelines and risks suspension

## Reviews

- [ ] Review generation process in place, and ethical/non-incentivized
- [ ] Review response process in place for both positive and negative reviews

## Off-Page

- [ ] Local link building / community engagement ongoing (chamber of commerce, local press, sponsorships)

## References

- [SEO Book, Chapter 19: Local SEO](../docs/books/complete/seo/chapter-19.md)
- `scripts/location_page_generator.py`, `scripts/service_page_generator.py` — the governed page templates referenced above
