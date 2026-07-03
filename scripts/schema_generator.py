"""Generate Schema.org JSON-LD structured data for common SEO page types.

Covers the schema types documented in ``docs/books/complete/seo/chapter-14.md``:
Article, Product, FAQPage, LocalBusiness, BreadcrumbList, and Organization.

Example:
    >>> from scripts.schema_generator import generate_article_schema, to_script_tag
    >>> schema = generate_article_schema(
    ...     headline="Core Web Vitals: A Complete Guide",
    ...     author_name="Jane Doe",
    ...     date_published="2026-01-15",
    ... )
    >>> print(to_script_tag(schema))
    <script type="application/ld+json">...</script>
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

SCHEMA_CONTEXT = "https://schema.org"


class SchemaValidationError(ValueError):
    """Raised when required fields for a schema type are missing or invalid."""


def _require(fields: dict[str, Any], required: list[str], schema_type: str) -> None:
    missing = [name for name in required if not fields.get(name)]
    if missing:
        raise SchemaValidationError(
            f"{schema_type} schema is missing required field(s): {', '.join(missing)}"
        )


def generate_article_schema(
    headline: str,
    author_name: str,
    date_published: str,
    *,
    date_modified: str | None = None,
    author_url: str | None = None,
    image: str | None = None,
    publisher_name: str | None = None,
    publisher_logo: str | None = None,
    article_type: str = "Article",
) -> dict[str, Any]:
    """Build an Article/NewsArticle/BlogPosting JSON-LD schema dict.

    Args:
        headline: The article's headline.
        author_name: Name of the author (required for E-E-A-T signals).
        date_published: ISO 8601 publish date (e.g. "2026-01-15").
        date_modified: ISO 8601 last-modified date.
        author_url: URL of the author's bio/profile page.
        image: Primary image URL for the article.
        publisher_name: Name of the publishing organization.
        publisher_logo: URL of the publisher's logo.
        article_type: One of "Article", "NewsArticle", "BlogPosting".

    Returns:
        A dict ready to be serialized as JSON-LD.

    Raises:
        SchemaValidationError: If headline, author_name, or date_published is missing.
    """
    fields = {"headline": headline, "author_name": author_name, "date_published": date_published}
    _require(fields, ["headline", "author_name", "date_published"], article_type)

    schema: dict[str, Any] = {
        "@context": SCHEMA_CONTEXT,
        "@type": article_type,
        "headline": headline,
        "datePublished": date_published,
        "author": {"@type": "Person", "name": author_name},
    }
    if author_url:
        schema["author"]["url"] = author_url
    if date_modified:
        schema["dateModified"] = date_modified
    if image:
        schema["image"] = image
    if publisher_name:
        publisher: dict[str, Any] = {"@type": "Organization", "name": publisher_name}
        if publisher_logo:
            publisher["logo"] = {"@type": "ImageObject", "url": publisher_logo}
        schema["publisher"] = publisher

    logger.debug("Generated %s schema for headline=%r", article_type, headline)
    return schema


def generate_product_schema(
    name: str,
    price: str,
    price_currency: str,
    *,
    sku: str | None = None,
    brand: str | None = None,
    availability: str = "InStock",
    rating_value: str | None = None,
    review_count: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Build a Product JSON-LD schema dict with an Offer and optional AggregateRating.

    Args:
        name: Product name.
        price: Price as a string, e.g. "129.99".
        price_currency: ISO 4217 currency code, e.g. "USD".
        sku: Stock keeping unit.
        brand: Brand name.
        availability: One of "InStock", "OutOfStock", "PreOrder", "Discontinued".
        rating_value: Average rating, e.g. "4.7".
        review_count: Number of reviews backing the rating.
        description: Product description.

    Returns:
        A dict ready to be serialized as JSON-LD.

    Raises:
        SchemaValidationError: If name, price, or price_currency is missing, or
            availability is not a recognized Schema.org value.
    """
    fields = {"name": name, "price": price, "price_currency": price_currency}
    _require(fields, ["name", "price", "price_currency"], "Product")

    valid_availability = {"InStock", "OutOfStock", "PreOrder", "Discontinued", "LimitedAvailability"}
    if availability not in valid_availability:
        raise SchemaValidationError(
            f"Invalid availability {availability!r}; must be one of {sorted(valid_availability)}"
        )

    schema: dict[str, Any] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Product",
        "name": name,
        "offers": {
            "@type": "Offer",
            "price": price,
            "priceCurrency": price_currency,
            "availability": f"{SCHEMA_CONTEXT}/{availability}",
        },
    }
    if sku:
        schema["sku"] = sku
    if brand:
        schema["brand"] = {"@type": "Brand", "name": brand}
    if description:
        schema["description"] = description
    if rating_value and review_count:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating_value,
            "reviewCount": review_count,
        }

    return schema


def generate_faq_schema(qa_pairs: list[tuple[str, str]]) -> dict[str, Any]:
    """Build a FAQPage JSON-LD schema dict from (question, answer) pairs.

    Args:
        qa_pairs: A non-empty list of (question, answer) string tuples.

    Returns:
        A dict ready to be serialized as JSON-LD.

    Raises:
        SchemaValidationError: If qa_pairs is empty or contains blank entries.
    """
    if not qa_pairs:
        raise SchemaValidationError("FAQPage schema requires at least one Q&A pair")

    main_entity = []
    for question, answer in qa_pairs:
        if not question.strip() or not answer.strip():
            raise SchemaValidationError("FAQPage entries must have non-empty question and answer")
        main_entity.append(
            {
                "@type": "Question",
                "name": question.strip(),
                "acceptedAnswer": {"@type": "Answer", "text": answer.strip()},
            }
        )

    return {"@context": SCHEMA_CONTEXT, "@type": "FAQPage", "mainEntity": main_entity}


def generate_local_business_schema(
    name: str,
    street_address: str,
    address_locality: str,
    address_region: str,
    postal_code: str,
    *,
    address_country: str = "US",
    telephone: str | None = None,
    business_type: str = "LocalBusiness",
    price_range: str | None = None,
) -> dict[str, Any]:
    """Build a LocalBusiness (or subtype) JSON-LD schema dict.

    Args:
        name: Business name.
        street_address: Street address line.
        address_locality: City/locality.
        address_region: State/region.
        postal_code: Postal/ZIP code.
        address_country: ISO 3166-1 alpha-2 country code.
        telephone: Business phone number.
        business_type: A Schema.org LocalBusiness subtype (e.g. "Dentist", "Restaurant").
        price_range: A price range indicator, e.g. "$$".

    Returns:
        A dict ready to be serialized as JSON-LD.

    Raises:
        SchemaValidationError: If any required address field is missing.
    """
    fields = {
        "name": name,
        "street_address": street_address,
        "address_locality": address_locality,
        "address_region": address_region,
        "postal_code": postal_code,
    }
    _require(
        fields,
        ["name", "street_address", "address_locality", "address_region", "postal_code"],
        business_type,
    )

    schema: dict[str, Any] = {
        "@context": SCHEMA_CONTEXT,
        "@type": business_type,
        "name": name,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": street_address,
            "addressLocality": address_locality,
            "addressRegion": address_region,
            "postalCode": postal_code,
            "addressCountry": address_country,
        },
    }
    if telephone:
        schema["telephone"] = telephone
    if price_range:
        schema["priceRange"] = price_range

    return schema


def generate_breadcrumb_schema(items: list[tuple[str, str | None]]) -> dict[str, Any]:
    """Build a BreadcrumbList JSON-LD schema dict.

    Args:
        items: An ordered list of (name, url) tuples from Home to the current
            page. The final item's url may be ``None`` (the current page is
            not required to link to itself).

    Returns:
        A dict ready to be serialized as JSON-LD.

    Raises:
        SchemaValidationError: If items is empty.
    """
    if not items:
        raise SchemaValidationError("BreadcrumbList schema requires at least one item")

    element_list = []
    for position, (name, url) in enumerate(items, start=1):
        entry: dict[str, Any] = {"@type": "ListItem", "position": position, "name": name}
        if url:
            entry["item"] = url
        element_list.append(entry)

    return {"@context": SCHEMA_CONTEXT, "@type": "BreadcrumbList", "itemListElement": element_list}


def generate_organization_schema(
    name: str,
    url: str,
    *,
    logo: str | None = None,
    same_as: list[str] | None = None,
) -> dict[str, Any]:
    """Build an Organization JSON-LD schema dict for sitewide brand identity.

    Args:
        name: Organization name.
        url: Canonical homepage URL.
        logo: URL of the organization's logo.
        same_as: URLs of authoritative external profiles (Wikipedia, Wikidata,
            verified social accounts) that establish entity identity.

    Returns:
        A dict ready to be serialized as JSON-LD.

    Raises:
        SchemaValidationError: If name or url is missing.
    """
    _require({"name": name, "url": url}, ["name", "url"], "Organization")

    schema: dict[str, Any] = {"@context": SCHEMA_CONTEXT, "@type": "Organization", "name": name, "url": url}
    if logo:
        schema["logo"] = logo
    if same_as:
        schema["sameAs"] = same_as
    return schema


def to_json_ld(schema: dict[str, Any], *, indent: int | None = 2) -> str:
    """Serialize a schema dict to a JSON-LD string.

    Args:
        schema: A schema dict, typically produced by one of the generator functions.
        indent: JSON indentation width. Use ``None`` for compact single-line output.

    Returns:
        The schema serialized as a JSON string.
    """
    return json.dumps(schema, indent=indent, ensure_ascii=False)


def to_script_tag(schema: dict[str, Any], *, indent: int | None = 2) -> str:
    """Wrap a schema dict in an ``<script type="application/ld+json">`` tag.

    Args:
        schema: A schema dict, typically produced by one of the generator functions.
        indent: JSON indentation width passed through to :func:`to_json_ld`.

    Returns:
        An HTML string containing the schema wrapped in a script tag.
    """
    return f'<script type="application/ld+json">\n{to_json_ld(schema, indent=indent)}\n</script>'


def combine_schemas(schemas: list[dict[str, Any]]) -> dict[str, Any]:
    """Combine multiple schema dicts into a single ``@graph`` document.

    Args:
        schemas: A list of schema dicts (each including its own ``@type``).
            Their ``@context`` keys are stripped and replaced by a single
            top-level context.

    Returns:
        A single dict with ``@context`` and ``@graph`` keys.

    Raises:
        SchemaValidationError: If schemas is empty.
    """
    if not schemas:
        raise SchemaValidationError("combine_schemas requires at least one schema")

    graph = [{k: v for k, v in schema.items() if k != "@context"} for schema in schemas]
    return {"@context": SCHEMA_CONTEXT, "@graph": graph}


def _build_arg_parser() -> Any:
    import argparse

    parser = argparse.ArgumentParser(description="Generate Schema.org JSON-LD markup.")
    sub = parser.add_subparsers(dest="schema_type", required=True)

    faq = sub.add_parser("faq", help="Generate FAQPage schema from a JSON file of Q&A pairs")
    faq.add_argument("json_file", help='Path to a JSON file: [["question", "answer"], ...]')

    article = sub.add_parser("article", help="Generate Article schema")
    article.add_argument("--headline", required=True)
    article.add_argument("--author", required=True)
    article.add_argument("--date-published", required=True)
    article.add_argument("--date-modified")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.schema_generator <schema_type> ...``."""
    logging.basicConfig(level=logging.INFO)
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    try:
        if args.schema_type == "faq":
            with open(args.json_file, encoding="utf-8") as f:
                pairs = [tuple(pair) for pair in json.load(f)]
            schema = generate_faq_schema(pairs)  # type: ignore[arg-type]
        elif args.schema_type == "article":
            schema = generate_article_schema(
                headline=args.headline,
                author_name=args.author,
                date_published=args.date_published,
                date_modified=args.date_modified,
            )
        else:  # pragma: no cover - argparse guarantees valid choices
            parser.error(f"Unknown schema type: {args.schema_type}")
            return 2
    except (SchemaValidationError, OSError, json.JSONDecodeError) as exc:
        logger.error("Schema generation failed: %s", exc)
        return 1

    print(to_script_tag(schema))
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
