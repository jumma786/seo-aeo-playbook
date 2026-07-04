# Technical SEO Checklist

Covers crawlability, indexability, site architecture, structured data, mobile, and international configuration. Where this repo's `seo-playbook` CLI can check an item directly, the command is noted — see the [CLI Reference](../docs/cli-reference.md).

## Crawlability & Indexability

- [ ] `robots.txt` reviewed for accidental blanket disallows — `seo-playbook robots` generates one from explicit rules, and `seo-playbook llms audit-crawlers` flags crawlers unintentionally caught by a `*` rule
- [ ] XML sitemap present, valid, and submitted in Search Console — `seo-playbook sitemap` generates one from a URL list
- [ ] No orphan pages among priority content — `seo-playbook link-suggestions` flags pages with zero inbound internal links
- [ ] No broken internal or outbound links — `seo-playbook check-links` audits a URL list or an HTML page's links, exiting non-zero in CI on any broken link
- [ ] Canonical tags present, self-referencing per page, and consistent between HTML and any sitemap/hreflang entries
- [ ] Noindex directives audited for pages that shouldn't be excluded — `seo-playbook audit` reports `is_noindex` per page

## Site Architecture

- [ ] Homepage-to-priority-page click depth is 3 or fewer
- [ ] Pillar-and-cluster model applied to core topic areas
- [ ] URL structure is lowercase, hyphenated, descriptive, and stable
- [ ] Faceted navigation controlled via robots/canonical rules
- [ ] Pagination independently crawlable with correct canonicals
- [ ] Programmatic/generated pages pass a minimum content-quality gate before publishing

## Structured Data

- [ ] JSON-LD format used for all new schema — `seo-playbook schema article|faq` generate it directly
- [ ] Core sitewide types implemented: `Organization`, `WebSite`, `BreadcrumbList`
- [ ] Content-type-specific schema implemented (`Article`, `Product`, `FAQPage`, `LocalBusiness`, etc.)
- [ ] Schema validated before and after deploy — `seo-playbook schema validate` checks a standalone schema file or every `<script type="application/ld+json">` block on a rendered page, and exits non-zero on error for CI gating
- [ ] Schema generation automated from CMS/database, not hand-written
- [ ] Search Console Enhancements monitored for errors post-launch

## Mobile

- [ ] Responsive design implemented sitewide
- [ ] Viewport meta tag present on every template
- [ ] Content, links, and schema verified identical between desktop and mobile DOM
- [ ] Tap targets meet minimum size and spacing guidelines
- [ ] No intrusive interstitials on mobile entry
- [ ] Mobile Core Web Vitals pass in field data (CrUX)
- [ ] Search Console Mobile Usability report shows zero errors

## Performance

- [ ] Render-blocking scripts/stylesheets minimized — `seo-playbook page-speed` flags render-blocking resources, images missing dimensions (CLS risk), and missing `loading="lazy"`
- [ ] Time-to-first-byte measured, not assumed — `page-speed` reports genuine TTFB via the server's actual response
- [ ] Core Web Vitals (LCP, INP, CLS) monitored via field data (CrUX/Search Console), not lab data alone

## International (if applicable)

- [ ] URL structure decided (subfolder/subdomain/ccTLD) and consistently applied
- [ ] hreflang implemented via one method only (head tags or sitemap, not both)
- [ ] Full reciprocity verified across the entire locale cluster
- [ ] `x-default` present
- [ ] Canonical tags are self-referencing per locale
- [ ] Content localized, not just machine-translated
- [ ] hreflang generation automated and validated in CI

## Full-Site Audit

- [ ] Run `seo-playbook site-audit urls.txt` across all priority pages — it runs the SEO, schema, and page-speed audits against a single fetch per page and rolls the results into a site-wide summary, exiting non-zero if any page fails to fetch or has schema errors

## References

- [SEO Book, Chapter 14: Structured Data & Schema Markup](../docs/books/complete/seo/chapter-14.md)
- [SEO Book, Chapter 15: Mobile SEO & Mobile-First Indexing](../docs/books/complete/seo/chapter-15.md)
- [SEO Book, Chapter 16: International SEO & Hreflang](../docs/books/complete/seo/chapter-16.md)
- [SEO Book, Chapter 17: Site Architecture & URL Structure](../docs/books/complete/seo/chapter-17.md)
