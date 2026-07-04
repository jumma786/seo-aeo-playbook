"""Unit tests for scripts.schema_generator."""

from __future__ import annotations

import json

import pytest

from scripts.schema_generator import (
    SchemaValidationError,
    combine_schemas,
    generate_article_schema,
    generate_breadcrumb_schema,
    generate_faq_schema,
    generate_local_business_schema,
    generate_organization_schema,
    generate_product_schema,
    to_json_ld,
    to_script_tag,
)


class TestArticleSchema:
    def test_minimal_valid_article(self) -> None:
        schema = generate_article_schema(
            headline="Core Web Vitals Guide",
            author_name="Jane Doe",
            date_published="2026-01-15",
        )
        assert schema["@type"] == "Article"
        assert schema["headline"] == "Core Web Vitals Guide"
        assert schema["author"] == {"@type": "Person", "name": "Jane Doe"}
        assert "dateModified" not in schema

    def test_full_article_with_publisher(self) -> None:
        schema = generate_article_schema(
            headline="Guide",
            author_name="Jane Doe",
            date_published="2026-01-15",
            date_modified="2026-06-01",
            author_url="https://example.com/authors/jane",
            image="https://example.com/img.jpg",
            publisher_name="Example Corp",
            publisher_logo="https://example.com/logo.png",
            article_type="BlogPosting",
        )
        assert schema["@type"] == "BlogPosting"
        assert schema["dateModified"] == "2026-06-01"
        assert schema["author"]["url"] == "https://example.com/authors/jane"
        assert schema["publisher"]["logo"]["url"] == "https://example.com/logo.png"

    @pytest.mark.parametrize("missing_field", ["headline", "author_name", "date_published"])
    def test_missing_required_field_raises(self, missing_field: str) -> None:
        kwargs = {
            "headline": "Guide",
            "author_name": "Jane Doe",
            "date_published": "2026-01-15",
        }
        kwargs[missing_field] = ""
        with pytest.raises(SchemaValidationError):
            generate_article_schema(**kwargs)


class TestProductSchema:
    def test_minimal_valid_product(self) -> None:
        schema = generate_product_schema(name="Trail Shoe", price="129.99", price_currency="USD")
        assert schema["offers"]["availability"] == "https://schema.org/InStock"
        assert "aggregateRating" not in schema

    def test_product_with_rating(self) -> None:
        schema = generate_product_schema(
            name="Trail Shoe",
            price="129.99",
            price_currency="USD",
            rating_value="4.7",
            review_count="182",
        )
        assert schema["aggregateRating"]["ratingValue"] == "4.7"
        assert schema["aggregateRating"]["reviewCount"] == "182"

    def test_invalid_availability_raises(self) -> None:
        with pytest.raises(SchemaValidationError):
            generate_product_schema(
                name="Trail Shoe", price="129.99", price_currency="USD", availability="Maybe"
            )

    def test_missing_price_raises(self) -> None:
        with pytest.raises(SchemaValidationError):
            generate_product_schema(name="Trail Shoe", price="", price_currency="USD")


class TestFaqSchema:
    def test_single_pair(self) -> None:
        schema = generate_faq_schema([("What is LCP?", "Largest Contentful Paint.")])
        assert schema["@type"] == "FAQPage"
        assert len(schema["mainEntity"]) == 1
        assert schema["mainEntity"][0]["name"] == "What is LCP?"
        assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == "Largest Contentful Paint."

    def test_empty_list_raises(self) -> None:
        with pytest.raises(SchemaValidationError):
            generate_faq_schema([])

    def test_blank_question_raises(self) -> None:
        with pytest.raises(SchemaValidationError):
            generate_faq_schema([("   ", "An answer")])


class TestLocalBusinessSchema:
    def test_minimal_valid(self) -> None:
        schema = generate_local_business_schema(
            name="Example Dental",
            street_address="123 Main St",
            address_locality="Austin",
            address_region="TX",
            postal_code="78701",
        )
        assert schema["@type"] == "LocalBusiness"
        assert schema["address"]["addressCountry"] == "US"

    def test_business_subtype(self) -> None:
        schema = generate_local_business_schema(
            name="Example Dental",
            street_address="123 Main St",
            address_locality="Austin",
            address_region="TX",
            postal_code="78701",
            business_type="Dentist",
        )
        assert schema["@type"] == "Dentist"

    def test_missing_address_field_raises(self) -> None:
        with pytest.raises(SchemaValidationError):
            generate_local_business_schema(
                name="Example Dental",
                street_address="",
                address_locality="Austin",
                address_region="TX",
                postal_code="78701",
            )


class TestBreadcrumbSchema:
    def test_ordered_positions(self) -> None:
        schema = generate_breadcrumb_schema(
            [("Home", "https://example.com/"), ("Blog", "https://example.com/blog/"), ("Post", None)]
        )
        positions = [item["position"] for item in schema["itemListElement"]]
        assert positions == [1, 2, 3]
        assert "item" not in schema["itemListElement"][2]

    def test_empty_list_raises(self) -> None:
        with pytest.raises(SchemaValidationError):
            generate_breadcrumb_schema([])


class TestOrganizationSchema:
    def test_with_same_as(self) -> None:
        schema = generate_organization_schema(
            name="Example Corp",
            url="https://example.com",
            same_as=["https://en.wikipedia.org/wiki/Example_Corp"],
        )
        assert schema["sameAs"] == ["https://en.wikipedia.org/wiki/Example_Corp"]


class TestSerialization:
    def test_to_json_ld_round_trips(self) -> None:
        schema = generate_organization_schema(name="Example Corp", url="https://example.com")
        parsed = json.loads(to_json_ld(schema))
        assert parsed == schema

    def test_to_script_tag_wraps_json(self) -> None:
        schema = generate_organization_schema(name="Example Corp", url="https://example.com")
        tag = to_script_tag(schema)
        assert tag.startswith('<script type="application/ld+json">')
        assert tag.endswith("</script>")
        assert "Example Corp" in tag

    def test_combine_schemas_single_context(self) -> None:
        org = generate_organization_schema(name="Example Corp", url="https://example.com")
        breadcrumb = generate_breadcrumb_schema([("Home", "https://example.com/")])
        combined = combine_schemas([org, breadcrumb])
        assert combined["@context"] == "https://schema.org"
        assert len(combined["@graph"]) == 2
        assert all("@context" not in entry for entry in combined["@graph"])

    def test_combine_schemas_empty_raises(self) -> None:
        with pytest.raises(SchemaValidationError):
            combine_schemas([])
