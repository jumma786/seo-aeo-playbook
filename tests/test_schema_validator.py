"""Unit tests for scripts.schema_validator."""

from __future__ import annotations

from scripts.schema_validator import (
    extract_json_ld_from_html,
    format_report,
    has_errors,
    validate_html,
    validate_schema,
)


class TestValidateSchemaGeneric:
    def test_missing_type_is_error(self) -> None:
        issues = validate_schema({"@context": "https://schema.org"})
        assert any(issue.path == "@type" and issue.severity == "error" for issue in issues)

    def test_missing_context_is_warning(self) -> None:
        issues = validate_schema({"@type": "Organization", "name": "Example Corp", "url": "https://example.com"})
        assert any(issue.path == "@context" and issue.severity == "warning" for issue in issues)

    def test_unknown_type_gets_info_notice_not_false_pass(self) -> None:
        issues = validate_schema({"@context": "https://schema.org", "@type": "Dentist", "name": "Smile Clinic"})
        assert len(issues) == 1
        assert issues[0].severity == "info"

    def test_graph_validates_each_nested_item(self) -> None:
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "Organization", "name": "Example Corp", "url": "https://example.com"},
                {"@type": "Article", "headline": "Hi"},
            ],
        }
        issues = validate_schema(schema)
        assert any(issue.path.startswith("@graph[1]") for issue in issues)
        assert not any(issue.path.startswith("@graph[0]") for issue in issues)

    def test_graph_not_a_list_is_error(self) -> None:
        issues = validate_schema({"@context": "https://schema.org", "@graph": "not-a-list"})
        assert len(issues) == 1
        assert issues[0].severity == "error"


class TestValidateArticle:
    def test_complete_article_has_no_issues(self) -> None:
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Core Web Vitals",
            "author": {"@type": "Person", "name": "Jane Doe"},
            "datePublished": "2026-01-15",
        }
        assert validate_schema(schema) == []

    def test_missing_fields_reported(self) -> None:
        issues = validate_schema({"@context": "https://schema.org", "@type": "Article", "headline": "Hi"})
        paths = {issue.path for issue in issues}
        assert paths == {"author", "datePublished"}

    def test_author_missing_name(self) -> None:
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Hi",
            "author": {"@type": "Person"},
            "datePublished": "2026-01-15",
        }
        issues = validate_schema(schema)
        assert any(issue.path == "author.name" for issue in issues)


class TestValidateProduct:
    def test_complete_product_has_no_issues(self) -> None:
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Trail Shoes",
            "offers": {"@type": "Offer", "price": "129.99", "priceCurrency": "USD"},
        }
        assert validate_schema(schema) == []

    def test_missing_offer_fields_reported(self) -> None:
        schema = {"@context": "https://schema.org", "@type": "Product", "name": "Trail Shoes", "offers": {}}
        issues = validate_schema(schema)
        paths = {issue.path for issue in issues}
        assert paths == {"offers.price", "offers.priceCurrency"}

    def test_non_dict_offers_is_warning(self) -> None:
        schema = {"@context": "https://schema.org", "@type": "Product", "name": "Trail Shoes", "offers": "129.99"}
        issues = validate_schema(schema)
        assert any(issue.path == "offers" and issue.severity == "warning" for issue in issues)


class TestValidateFaqPage:
    def test_complete_faq_has_no_issues(self) -> None:
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "What is SEO?", "acceptedAnswer": {"@type": "Answer", "text": "..."}}
            ],
        }
        assert validate_schema(schema) == []

    def test_empty_main_entity_is_error(self) -> None:
        issues = validate_schema({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": []})
        assert len(issues) == 1
        assert issues[0].path == "mainEntity"

    def test_entry_missing_accepted_answer(self) -> None:
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": "What is SEO?"}],
        }
        issues = validate_schema(schema)
        assert any(issue.path == "mainEntity[0].acceptedAnswer.text" for issue in issues)


class TestValidateBreadcrumbList:
    def test_missing_items_is_error(self) -> None:
        issues = validate_schema({"@context": "https://schema.org", "@type": "BreadcrumbList"})
        assert len(issues) == 1
        assert issues[0].path == "itemListElement"


class TestHasErrors:
    def test_true_when_error_present(self) -> None:
        issues = validate_schema({"@context": "https://schema.org", "@type": "Article", "headline": "Hi"})
        assert has_errors(issues) is True

    def test_false_when_only_warnings_or_none(self) -> None:
        schema = {"@type": "Organization", "name": "Example Corp", "url": "https://example.com"}
        assert has_errors(validate_schema(schema)) is False


class TestExtractJsonLdFromHtml:
    def test_extracts_valid_block(self) -> None:
        html = '<html><head><script type="application/ld+json">{"@type": "Organization", "name": "X"}</script></head></html>'
        schemas = extract_json_ld_from_html(html)
        assert schemas == [{"@type": "Organization", "name": "X"}]

    def test_skips_malformed_block(self) -> None:
        html = '<script type="application/ld+json">{not valid json}</script>'
        assert extract_json_ld_from_html(html) == []

    def test_no_script_tags_returns_empty(self) -> None:
        assert extract_json_ld_from_html("<html><body>hi</body></html>") == []

    def test_multiple_blocks_extracted_in_order(self) -> None:
        html = (
            '<script type="application/ld+json">{"@type": "Organization", "name": "A"}</script>'
            '<script type="application/ld+json">{"@type": "Organization", "name": "B"}</script>'
        )
        schemas = extract_json_ld_from_html(html)
        assert [s["name"] for s in schemas] == ["A", "B"]


class TestValidateHtml:
    def test_validates_each_extracted_block(self) -> None:
        html = '<script type="application/ld+json">{"@type": "Article", "headline": "Hi"}</script>'
        results = validate_html(html)
        assert len(results) == 1
        paths = {issue.path for issue in results[0][1]}
        assert paths == {"author", "datePublished", "@context"}


class TestFormatReport:
    def test_reports_ok_when_no_issues(self) -> None:
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Example Corp",
            "url": "https://example.com",
        }
        report = format_report([(schema, validate_schema(schema))])
        assert "OK - no issues found" in report

    def test_reports_issue_details(self) -> None:
        schema = {"@context": "https://schema.org", "@type": "Article", "headline": "Hi"}
        report = format_report([(schema, validate_schema(schema))])
        assert "[ERROR]" in report
        assert "author" in report
