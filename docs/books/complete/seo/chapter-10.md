# Chapter 10: Entity SEO

**Version:** 1.0

---

# Table of Contents

1. Introduction
2. What is an Entity?
3. Entity vs Keyword
4. Why Entities Matter
5. Google's Knowledge Graph
6. Named Entities
7. Entity Relationships
8. Semantic Search
9. Topic Clusters
10. Topical Authority
11. Entity Recognition
12. Structured Data
13. Schema.org
14. JSON-LD
15. Organization Entity
16. Person Entity
17. Product Entity
18. Local Business Entity
19. Article Entity
20. FAQ Entity
21. Breadcrumb Entity
22. AI Search
23. AEO
24. GEO
25. Entity Optimization Checklist
26. Best Practices
27. Summary
28. References

---

# 1. Introduction

Entity SEO focuses on helping search engines understand real-world people, places, organizations, products, concepts, and events instead of relying only on keywords. Modern search engines use entities and their relationships to better understand content and provide more relevant results.

---

# 2. What is an Entity?

An entity is any distinct, identifiable thing content refers to — a person, organization, place, product, or concept — with a stable identity independent of the specific words used to describe it. "Apple the company" and "Apple the fruit" are different entities that happen to share a name; "Tim Cook" and "the CEO of Apple" are the same entity described two different ways.

---

# 3. Entity vs Keyword

A keyword is a string of text someone might search for; an entity is the real-world thing that string might refer to. "Running shoes" is a topic/keyword; "TrailCo" (a specific brand) or "Boston Marathon" (a specific event) are entities with a referenceable identity a search engine can look up in a knowledge base like Wikidata.

---

# 4. Why Entities Matter

Entity SEO helps:

- Improve topical authority
- Strengthen semantic relevance
- Increase AI search visibility
- Support knowledge graph inclusion
- Improve structured search results
- Enhance content understanding

---

# 5. Google's Knowledge Graph

Google's Knowledge Graph is a database of entities and the relationships between them, powering features like Knowledge Panels and helping Google disambiguate ambiguous queries. Entities in the Knowledge Graph are typically backed by structured sources like Wikipedia and Wikidata, and reinforced by consistent `sameAs` links from a brand's own site.

---

# 6. Named Entities

Named Entity Recognition (NER) is the task of identifying entity mentions in text and classifying their type (Person, Organization, Place, Date, and so on) — typically the first processing step in building or querying a knowledge graph. `scripts/entity_extractor.py` in this repository implements a lightweight version of this for content audits; run it via `seo-playbook entities <file>`.

---

# 7. Entity Relationships

Entities rarely stand alone — a knowledge graph represents them as nodes connected by typed relationships ("works for," "located in," "manufactured by"). Content that makes these relationships explicit (naming both entities and how they relate) is easier for a search engine to map onto its own graph. See the [GEO Book, Chapter 2: Knowledge Graphs](../geo/chapter-02.md) for the underlying data structure.

---

# 8. Semantic Search

Semantic search matches meaning and entity identity rather than exact keyword strings — understanding that a query about "the iPhone maker's CEO" and "Tim Cook" are asking about the same entity. See [Chapter 9, Section 10](chapter-09.md) and the [GEO Book, Chapter 4](../geo/chapter-04.md).

---

# 9. Topic Clusters

Entities and topic clusters reinforce each other: a pillar-and-cluster content architecture ([Chapter 17](chapter-17.md)) naturally produces a dense, consistent set of entity mentions and relationships around a subject area, which is exactly what strengthens topical authority in a search engine's eyes.

---

# 10. Topical Authority

Topical authority is earned when a site consistently, accurately, and comprehensively covers the entities and relationships within a subject area over time — not from a single page, but from the accumulated, interlinked coverage of a whole topic cluster. See [Chapter 6, Section 20](chapter-06.md).

---

# 11. Entity Recognition

Beyond a search engine's own internal NER systems, you can audit your own content's entity coverage directly: `seo-playbook entities <content>` extracts named entities and a frequency-based salience score, and `--compare <competitor-content>` surfaces entities a competitor mentions that you don't — a mechanical version of entity gap analysis.

---

# 12. Structured Data

Structured data is the mechanical bridge between prose mentioning an entity and a search engine's confident identification of it — explicitly declaring "this page is about an Organization named X, with this URL and these sameAs links" rather than leaving it to be inferred from text. See [Chapter 14](chapter-14.md).

---

# 13. Schema.org

Schema.org is the shared vocabulary most structured data on the web uses — a standardized set of types (`Organization`, `Person`, `Product`, `Article`, and hundreds more) and properties that search engines across Google, Bing, and others agree to interpret consistently.

---

# 14. JSON-LD

JSON-LD is Google's recommended format for implementing Schema.org markup — a self-contained `<script type="application/ld+json">` block that doesn't require altering visible HTML. `scripts/schema_generator.py` in this repository generates JSON-LD for the entity types below, and `scripts/schema_validator.py` validates it; both are wrapped by `seo-playbook schema`.

---

# 15. Organization Entity

`Organization` schema establishes a business's canonical entity identity — name, URL, logo, and `sameAs` links to authoritative external profiles (Wikipedia, Wikidata, verified social accounts) that help a search engine confirm the entity's identity beyond your own site's say-so.

---

# 16. Person Entity

`Person` schema (often nested inside `Article` as `author`) establishes an individual's identity and, combined with a real author bio page, supports E-E-A-T signals ([Chapter 12](chapter-12.md)) by making expertise attributable to a specific, identifiable person rather than an anonymous byline.

---

# 17. Product Entity

`Product` schema declares a specific product's identity along with machine-readable facts — price, availability, rating — that AI systems and rich results can quote directly rather than having to parse from prose. Schema must match the visible page content exactly; mismatched schema/content is a Google guidelines violation.

---

# 18. Local Business Entity

`LocalBusiness` schema (and its many subtypes — `Restaurant`, `Dentist`, and others) establishes a physical or service-area business's entity identity, including NAP (Name, Address, Phone) data. See [Chapter 19](chapter-19.md) and `seo-playbook location-pages`/`service-pages` for governed, quality-gated generation of this schema at scale.

---

# 19. Article Entity

`Article` schema (and its subtypes `NewsArticle`, `BlogPosting`) declares a piece of content's headline, author, and publication/modification dates — reinforcing both entity identity (who wrote this) and E-E-A-T trust signals.

---

# 20. FAQ Entity

`FAQPage` schema structures genuine question/answer pairs as discrete, machine-readable entities in their own right — each question and its accepted answer individually addressable, which is part of why well-structured FAQ content performs well for both Featured Snippets and AI citation. `scripts/faq_generator.py` generates this schema alongside citability-validated Markdown; see [Chapter 9, Section 20](chapter-09.md).

---

# 21. Breadcrumb Entity

`BreadcrumbList` schema declares a page's position within a site's hierarchy as a structured, ordered list of entities — reinforcing site architecture ([Chapter 17](chapter-17.md)) in machine-readable form and typically improving how a URL displays in search results.

---

# 22. AI Search

AI answer engines lean heavily on entity understanding to disambiguate queries and ground generated answers in specific, verifiable facts about specific things — an entity-rich, well-linked page is inherently easier for an AI system to confidently cite than one relying on vague, un-named references. See the [AEO Book](../aeo/README.md).

---

# 23. AEO

Answer Engine Optimization builds directly on entity SEO: naming entities explicitly (not "it" or "the company"), linking them to authoritative sources, and reinforcing them with structured data all improve the odds an AI answer engine can confidently retrieve and cite a passage. See [AEO Book, Chapter 7](../aeo/chapter-07.md).

---

# 24. GEO

Generative Engine Optimization goes deeper into the mechanics: how entities are represented as embeddings, linked within a knowledge graph, and retrieved via vector search to ground an LLM's generated answer. See the [GEO Book, Chapters 2-3](../geo/chapter-02.md) for knowledge graphs and entity linking specifically.

---

# 25. Entity Optimization Checklist

- [ ] Key entities named explicitly and consistently, not referred to only by pronoun after first mention
- [ ] `Organization`/`Person` schema includes `sameAs` links to authoritative external profiles
- [ ] Entity-relevant schema type applied per page (`Article`, `Product`, `LocalBusiness`, `FAQPage`) and validated — `seo-playbook schema validate`
- [ ] Entity coverage checked against competitor content — `seo-playbook entities --compare`
- [ ] High-salience entities reflected in titles, headings, and structured data, not just buried in body text

---

# 26. Best Practices

- Name entities explicitly and consistently rather than relying on pronouns or vague references
- Use full, canonical entity names on first mention in a section, not just abbreviations
- Link entity mentions to their own authoritative pages (internal team/product pages, external Wikipedia/Wikidata)
- Reinforce every entity mention that matters with matching structured data
- Audit entity coverage against competitors periodically, not just keyword coverage

---

# Summary

Entity SEO shifts the unit of optimization from keyword strings to real-world things and their relationships — the same shift that underlies modern semantic search, knowledge graphs, and AI answer engines. Naming entities explicitly, linking them to authoritative sources, and reinforcing them with accurate structured data is what lets both traditional and AI search systems confidently understand and cite content, rather than merely matching its words.

---

# Learning Outcomes

After completing this chapter, you will understand:

- What entities are
- How knowledge graphs work
- Entity-based optimization
- Structured data implementation
- Entity SEO for AI search

---

# References

- Google Search Central: Understand How Structured Data Works
- Wikidata Query Service Documentation

---

**Next:** Chapter 11 – Internal Linking
