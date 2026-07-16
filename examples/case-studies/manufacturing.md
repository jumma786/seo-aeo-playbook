# Case Study: Industrial Manufacturing

> **This is an illustrative, composite example for demonstration purposes.** "Ridgeline Fabrication" is a fictional company; it does not describe any real business's actual results. It walks through how the frameworks and tools in this repository would apply to a typical B2B manufacturing site, not a documented outcome.

## Business Profile

Ridgeline Fabrication is a mid-size contract manufacturer producing custom sheet-metal and CNC-machined parts for industrial clients. Like most B2B manufacturers, their buyers are engineers and procurement teams doing extensive research before ever contacting sales — making organic search a critical, under-invested channel relative to their trade-show and referral-driven history.

## Starting Situation

- A single, thin "Capabilities" page listing services with no depth per service
- No structured data anywhere on the site
- Zero content addressing the specific technical questions engineers actually search (tolerances, material specs, minimum order quantities)
- No presence in AI answer engines for comparison queries ("CNC machining vs sheet metal fabrication")

## Applying the SEO Book

**Site architecture ([Chapter 17](../../docs/books/complete/seo/chapter-17.md)):** Replaced the single Capabilities page with a pillar-and-cluster structure — a "Manufacturing Capabilities" pillar page linking to dedicated cluster pages per service (CNC Machining, Sheet Metal Fabrication, Welding, Finishing), each targeting the specific technical keywords engineers search. See the [Pillar Page Template](../../templates/pillar-page-template.md).

**Keyword research ([Chapter 8](../../docs/books/complete/seo/chapter-08.md)):** Seed terms ("CNC machining," "sheet metal fabrication") expanded into long-tail technical queries ("CNC machining tolerances for aluminum 6061," "minimum order quantity sheet metal prototyping") using `seo-playbook cluster` to group them into the cluster pages above.

**Schema markup ([Chapter 14](../../docs/books/complete/seo/chapter-14.md)):** Added `Organization` schema sitewide, `Product`/`Service` schema per capability page, and `LocalBusiness` schema for the physical facility — generated and validated with `seo-playbook schema` and `schema validate`.

**Technical foundation:** Ran `seo-playbook site-audit` across every priority page to catch on-page and schema issues before investing further in content, and `seo-playbook sitemap`/`robots` to ensure the new cluster pages were properly discoverable.

## Applying the AEO/GEO Books

B2B buyers frequently start research in ChatGPT or Perplexity with comparison queries ("what's the difference between CNC machining and sheet metal fabrication for low-volume parts"). Following [AEO Book, Chapter 7](../../docs/books/complete/aeo/chapter-07.md), each cluster page was restructured to lead with a direct, self-contained answer to its core question before supporting detail, naming the process explicitly rather than opening with a dangling pronoun.

An `llms.txt` file was published (`seo-playbook llms generate`) curating links to the pillar page and each capability cluster page, and `seo-playbook llms audit-crawlers` confirmed no AI crawler was being unintentionally blocked by an overly broad legacy `robots.txt` rule.

## Illustrative Outcome

In a scenario like this, the expected qualitative impact is: technical buyers finding specific capability pages that directly answer their spec questions (rather than bouncing off a thin generic page), reduced sales-team time spent answering questions already covered on-site, and improved odds of being cited when a buyer researches via an AI answer engine before ever reaching out. This case study does not report specific traffic or ranking numbers, since none were measured for a fictional example — treat any numeric claims you see elsewhere as illustrative unless a source is cited.

## Tools referenced in this case study

`seo-playbook cluster`, `content-brief`, `schema article|faq`, `schema validate`, `sitemap`, `robots`, `site-audit`, `llms generate`, `llms audit-crawlers` — see the [CLI Reference](../../docs/cli-reference.md).
