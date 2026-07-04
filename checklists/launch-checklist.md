# Website Launch Checklist

A pre-launch/post-launch gate pulling the highest-priority items from the other checklists in this directory. Run through this before flipping a new site (or major redesign) live, and again immediately after.

## Before Launch

- [ ] Staging environment fully blocked from indexing (`robots.txt` disallow-all or `noindex`, confirmed removed before go-live)
- [ ] Production `robots.txt` reviewed for accidental blanket disallows — `seo-playbook robots`
- [ ] XML sitemap generated and ready to submit — `seo-playbook sitemap`
- [ ] `llms.txt` published if the site is documentation/content-heavy — `seo-playbook llms generate`
- [ ] Every priority page has a unique title (30-60 chars) and meta description (70-160 chars) — see [On-Page Checklist](on-page.md)
- [ ] Every priority page has a single `<h1>` and a logical heading hierarchy
- [ ] Core sitewide schema in place: `Organization`, `WebSite`, `BreadcrumbList` — validated with `seo-playbook schema validate`
- [ ] 301 redirect map complete for every URL that's changing or being retired (migrations only)
- [ ] No broken internal links — `seo-playbook check-links`
- [ ] No orphan pages among priority content — `seo-playbook link-suggestions`
- [ ] HTTPS enforced sitewide, no mixed content
- [ ] Responsive design verified on real mobile devices, not just browser resize
- [ ] Analytics (GA4) and Search Console installed and verified before launch, not after

## At Launch

- [ ] Staging blocks removed; production `robots.txt` confirmed live and correct
- [ ] Sitemap submitted in Search Console
- [ ] Full-site audit run against the live URLs — `seo-playbook site-audit urls.txt` (SEO + schema + page-speed in one pass, exits non-zero on fetch failures or schema errors)
- [ ] Redirects spot-checked live, not just in the map

## First Week Post-Launch

- [ ] Search Console coverage report checked daily for crawl errors or unexpected exclusions
- [ ] Core Web Vitals field data starting to populate (CrUX takes ~28 days for full field data, but check early trends)
- [ ] Rank tracking baseline established for priority keywords
- [ ] Redirect map monitored for 404s slipping through

## References

- [Technical SEO Checklist](technical-seo.md)
- [On-Page SEO Checklist](on-page.md)
- [SEO Book, Chapter 17: Site Architecture & URL Structure](../docs/books/complete/seo/chapter-17.md)
- [SEO Book, Chapter 20: SEO Analytics & Measuring Success](../docs/books/complete/seo/chapter-20.md)
