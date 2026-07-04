# E-E-A-T Checklist

E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) is the framework from Google's Search Quality Rater Guidelines used to assess content and site quality — most heavily weighted for YMYL ("Your Money or Your Life") topics like health, finance, and legal advice, but a good practice sitewide. It matters for AI answer engines too: several AEO chapters in this repo (see References) note that clear authorship and dates reinforce the same trust signals answer engines look for when deciding what to cite.

> **Note:** SEO Book Chapter 12 (E-E-A-T) is currently an incomplete stub in this repo — this checklist is written from the established public framework, not extracted from that chapter. See the repo roadmap for the chapter-completion backlog.

## Experience

- [ ] Content demonstrates first-hand experience with the topic where relevant (product reviews, how-tos, personal case studies), not just aggregated research
- [ ] Original photos, data, or examples used instead of generic stock content where experience is being claimed

## Expertise

- [ ] Author bylines present on content where expertise matters (not anonymous/unattributed)
- [ ] Author bio pages exist and describe relevant credentials or experience
- [ ] For YMYL topics specifically, content is written or reviewed by someone with demonstrable subject-matter expertise

## Authoritativeness

- [ ] Site/author has recognizable citations, mentions, or backlinks from other authoritative sources in the field
- [ ] Entity presence established — consistent `sameAs` links to Wikipedia/Wikidata/verified social profiles where applicable ([Organization schema](../docs/books/complete/seo/chapter-14.md))
- [ ] Consistent, canonical naming of the organization/author across the site and external profiles

## Trustworthiness

- [ ] HTTPS sitewide, no mixed content
- [ ] Contact information, business details, and policies (privacy, returns, terms) easily findable
- [ ] Publication and last-modified dates visible on content, and accurate — not artificially bumped without a real update
- [ ] Reviews and testimonials are genuine and not fabricated or incentivized
- [ ] Sources cited for factual claims, especially statistics and YMYL content

## Structured Data Support

- [ ] `Article` schema includes `author`, `datePublished`, and `dateModified`
- [ ] `Organization` schema present sitewide with logo and `sameAs` links — `seo-playbook schema` can generate this

## References

- [AEO Book, Chapter 7: AI Citations & Passage-Level Citability](../docs/books/complete/aeo/chapter-07.md) — cross-references E-E-A-T as a citability trust signal
- Google Search Quality Rater Guidelines (public documentation, not part of this repo)
