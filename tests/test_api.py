"""Unit tests for the FastAPI app (api/app.py, api/routes.py)."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest
import requests
from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)

GOOD_FAQ_ANSWER = "SEO is the practice of optimizing a website so it ranks higher in organic search engine results pages."


class TestHealth:
    def test_health_check(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestOpenApi:
    def test_openapi_schema_generates(self) -> None:
        assert client.get("/openapi.json").status_code == 200

    def test_docs_ui_loads(self) -> None:
        assert client.get("/docs").status_code == 200


class TestSchemaEndpoints:
    def test_article_schema(self) -> None:
        response = client.post(
            "/schema/article",
            json={"headline": "Core Web Vitals", "author_name": "Jane Doe", "date_published": "2026-01-15"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["schema"]["headline"] == "Core Web Vitals"
        assert "<script" in body["script_tag"]

    def test_article_schema_missing_field_is_400(self) -> None:
        response = client.post("/schema/article", json={"headline": "Only headline", "author_name": "", "date_published": ""})
        assert response.status_code == 400

    def test_faq_schema(self) -> None:
        response = client.post("/schema/faq", json={"pairs": [{"question": "What is SEO?", "answer": GOOD_FAQ_ANSWER}]})
        assert response.status_code == 200
        assert response.json()["schema"]["@type"] == "FAQPage"

    def test_validate_schema_object(self) -> None:
        response = client.post(
            "/schema/validate",
            json={"schema": {"@context": "https://schema.org", "@type": "Article", "headline": "Hi"}},
        )
        assert response.status_code == 200
        assert response.json()["has_errors"] is True

    def test_validate_html(self) -> None:
        html = '<script type="application/ld+json">{"@context": "https://schema.org", "@type": "Organization", "name": "X", "url": "https://example.com"}</script>'
        response = client.post("/schema/validate", json={"html": html})
        assert response.status_code == 200
        assert response.json()["has_errors"] is False

    def test_validate_neither_provided_is_400(self) -> None:
        assert client.post("/schema/validate", json={}).status_code == 400


class TestAuditEndpoints:
    def test_audit_seo(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import api.routes as routes_module

        html = "<html><head><title>" + ("A" * 40) + "</title></head><body><h1>Hi</h1></body></html>"
        fake_response = SimpleNamespace(text=html, raise_for_status=lambda: None)
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: fake_response)
        response = client.post("/audit/seo", json={"url": "https://example.com/"})
        assert response.status_code == 200
        assert response.json()["url"] == "https://example.com/"

    def test_audit_seo_fetch_failure_is_502(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fail(url: str, **kwargs: object) -> None:
            raise requests.ConnectionError("refused")

        monkeypatch.setattr(requests, "get", fail)
        response = client.post("/audit/seo", json={"url": "https://example.com/"})
        assert response.status_code == 502

    def test_audit_page_speed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_response = SimpleNamespace(
            text="<html><body>hi</body></html>", elapsed=timedelta(seconds=0.2), raise_for_status=lambda: None
        )
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: fake_response)
        response = client.post("/audit/page-speed", json={"url": "https://example.com/"})
        assert response.status_code == 200
        assert response.json()["ttfb_seconds"] == pytest.approx(0.2)

    def test_audit_site(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_response = SimpleNamespace(
            text="<html><head><title>" + ("A" * 40) + "</title></head><body>hi</body></html>",
            elapsed=timedelta(seconds=0.1),
            raise_for_status=lambda: None,
        )
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: fake_response)
        response = client.post("/audit/site", json={"urls": ["https://example.com/"]})
        assert response.status_code == 200
        body = response.json()
        assert body["total_pages"] == 1
        assert body["pages"][0]["ok"] is True

    def test_audit_links_with_url_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "head", lambda url, **kwargs: SimpleNamespace(status_code=200, url=url, history=[]))
        response = client.post("/audit/links", json={"urls": ["https://example.com/"]})
        assert response.status_code == 200
        assert response.json()["broken_count"] == 0

    def test_audit_links_with_html(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "head", lambda url, **kwargs: SimpleNamespace(status_code=200, url=url, history=[]))
        response = client.post("/audit/links", json={"html": '<a href="/about">About</a>', "base_url": "https://example.com/"})
        assert response.status_code == 200

    def test_audit_links_neither_provided_is_400(self) -> None:
        assert client.post("/audit/links", json={}).status_code == 400


class TestSitemapRobotsLlms:
    def test_sitemap(self) -> None:
        response = client.post("/sitemap", json={"urls": [{"loc": "https://example.com/"}]})
        assert response.status_code == 200
        assert "<urlset" in response.json()["xml"]

    def test_sitemap_invalid_url_is_400(self) -> None:
        response = client.post("/sitemap", json={"urls": [{"loc": "not-a-url"}]})
        assert response.status_code == 400

    def test_robots(self) -> None:
        response = client.post("/robots", json={"groups": [{"user_agent": "*", "disallow": ["/admin/"]}]})
        assert response.status_code == 200
        assert "Disallow: /admin/" in response.json()["content"]

    def test_llms_generate(self) -> None:
        response = client.post(
            "/llms/generate",
            json={
                "name": "Example Corp",
                "summary": "A short summary.",
                "sections": [{"heading": "Docs", "links": [{"title": "Start", "url": "https://example.com/"}]}],
            },
        )
        assert response.status_code == 200
        assert "# Example Corp" in response.json()["content"]

    def test_llms_audit_crawlers(self) -> None:
        response = client.post("/llms/audit-crawlers", json={"robots_txt": "User-agent: *\nDisallow: /\n"})
        assert response.status_code == 200
        body = response.json()
        assert body["blocked_count"] == len(body["statuses"])


class TestKeywordEndpoints:
    def test_cluster(self) -> None:
        response = client.post("/keywords/cluster", json={"keywords": ["running shoes", "best running shoes"]})
        assert response.status_code == 200
        assert len(response.json()["clusters"]) >= 1

    def test_map_audit_finds_cannibalization(self) -> None:
        response = client.post(
            "/keywords/map/audit",
            json={"mappings": [{"keyword": "shoes", "url": "/a"}, {"keyword": "shoes", "url": "/b"}]},
        )
        assert response.status_code == 200
        assert len(response.json()["issues"]) == 1

    def test_map_suggest(self) -> None:
        response = client.post(
            "/keywords/map/suggest",
            json={"keywords": ["core web vitals"], "pages": {"/cwv": "Core Web Vitals Guide"}},
        )
        assert response.status_code == 200
        assert response.json()["mappings"][0]["url"] == "/cwv"


class TestEntitiesAndLinking:
    def test_extract_entities(self) -> None:
        response = client.post("/entities/extract", json={"text": "Jane Doe joined Example Corp in 2024."})
        assert response.status_code == 200
        assert len(response.json()["mentions"]) > 0

    def test_extract_entities_with_gaps(self) -> None:
        response = client.post(
            "/entities/extract",
            json={"text": "Example Corp builds tools.", "compare_text": "TrailCo builds tools."},
        )
        assert response.status_code == 200
        assert "TrailCo" in response.json()["gaps"]

    def test_links_suggest(self) -> None:
        response = client.post(
            "/links/suggest",
            json={
                "pages": [
                    {"url": "/guide", "title": "SEO Guide", "body": "See Core Web Vitals."},
                    {"url": "/cwv", "title": "Core Web Vitals"},
                ]
            },
        )
        assert response.status_code == 200
        assert len(response.json()["suggestions"]) == 1


class TestContentEndpoints:
    def test_meta_title_and_description(self) -> None:
        response = client.post("/meta", json={"title": "Core Web Vitals", "brand": "Example Corp"})
        assert response.status_code == 200
        assert "Example Corp" in response.json()["title"]

    def test_meta_neither_provided_is_400(self) -> None:
        assert client.post("/meta", json={}).status_code == 400

    def test_content_brief(self) -> None:
        response = client.post(
            "/content-brief",
            json={"primary_keyword": "core web vitals", "related_keywords": ["lcp guide"], "target_word_count": 1000},
        )
        assert response.status_code == 200
        assert response.json()["primary_keyword"] == "core web vitals"

    def test_faq(self) -> None:
        response = client.post("/faq", json={"items": [{"question": "What is SEO?", "answer": GOOD_FAQ_ANSWER}]})
        assert response.status_code == 200
        assert "FAQPage" in response.json()["schema_tag"]

    def test_blog_scaffold(self) -> None:
        response = client.post(
            "/blog-scaffold",
            json={
                "title": "Core Web Vitals Explained",
                "slug": "core-web-vitals-explained",
                "author_name": "Jane Doe",
                "date_published": "2026-01-15",
                "primary_keyword": "core web vitals",
            },
        )
        assert response.status_code == 200
        assert "Core Web Vitals Explained" in response.json()["markdown"]


class TestLocalSeoEndpoints:
    GOOD_CONTENT = " ".join(["Our Austin location offers great service"] * 10)

    def _nap(self) -> dict:
        return {
            "name": "Example Dental",
            "street_address": "1 Main St",
            "address_locality": "Austin",
            "address_region": "TX",
            "postal_code": "78701",
            "telephone": "512-555-0100",
        }

    def test_location_pages(self) -> None:
        response = client.post(
            "/local/location-pages",
            json={"specs": [{"url_slug": "austin-tx", "nap": self._nap(), "unique_content": self.GOOD_CONTENT}]},
        )
        assert response.status_code == 200
        assert "austin-tx" in response.json()["pages"]

    def test_location_pages_quality_gate_failure_is_422(self) -> None:
        response = client.post(
            "/local/location-pages",
            json={"specs": [{"url_slug": "austin-tx", "nap": self._nap(), "unique_content": "Too short."}]},
        )
        assert response.status_code == 422

    def test_service_pages(self) -> None:
        response = client.post(
            "/local/service-pages",
            json={
                "specs": [
                    {
                        "url_slug": "austin-tx-plumbing",
                        "business_name": "Example Plumbing",
                        "service_name": "Emergency Plumbing",
                        "area_served": "Austin, TX",
                        "telephone": "512-555-0100",
                        "unique_content": self.GOOD_CONTENT,
                    }
                ]
            },
        )
        assert response.status_code == 200
        content = response.json()["pages"]["austin-tx-plumbing"]
        assert "streetAddress" not in content


class TestBookDocsEndpoints:
    SAMPLE_CHAPTER = (
        "# Chapter 1: Example Chapter\n\n**Version:** 1.0\n\n---\n\n# Table of Contents\n\n1. Intro\n\n---\n\n"
        "# 1. Intro\n\nThis chapter covers the basics of the topic. More detail follows.\n"
    )

    def test_toc(self) -> None:
        response = client.post("/book-docs/toc", json={"chapters": [{"filename": "chapter-01.md", "content": self.SAMPLE_CHAPTER}]})
        assert response.status_code == 200
        assert "chapter-01.md" in response.json()["table"]

    def test_readme(self) -> None:
        response = client.post(
            "/book-docs/readme",
            json={
                "title": "The Example Book",
                "description": "A short description.",
                "chapters": [{"filename": "chapter-01.md", "content": self.SAMPLE_CHAPTER}],
            },
        )
        assert response.status_code == 200
        assert response.json()["readme"].startswith("# The Example Book")

    def test_toc_bad_chapter_is_400(self) -> None:
        response = client.post("/book-docs/toc", json={"chapters": [{"filename": "bad.md", "content": "no heading here"}]})
        assert response.status_code == 400
