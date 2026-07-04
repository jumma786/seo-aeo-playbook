"""Unit tests for scripts.sitemap_generator."""

from __future__ import annotations

from datetime import date

import pytest

from scripts.sitemap_generator import (
    MAX_URLS_PER_SITEMAP,
    SitemapURL,
    SitemapValidationError,
    generate_sitemap,
    generate_sitemap_index,
    generate_sitemaps,
)


class TestSitemapURL:
    def test_valid_url_accepted(self) -> None:
        url = SitemapURL(loc="https://example.com/")
        assert url.loc == "https://example.com/"

    def test_relative_url_rejected(self) -> None:
        with pytest.raises(SitemapValidationError):
            SitemapURL(loc="/relative-path")

    def test_invalid_changefreq_rejected(self) -> None:
        with pytest.raises(SitemapValidationError):
            SitemapURL(loc="https://example.com/", changefreq="sometimes")

    def test_priority_out_of_range_rejected(self) -> None:
        with pytest.raises(SitemapValidationError):
            SitemapURL(loc="https://example.com/", priority=1.5)

    def test_to_xml_with_date_lastmod(self) -> None:
        url = SitemapURL(loc="https://example.com/", lastmod=date(2026, 1, 15), priority=0.8)
        xml = url.to_xml()
        assert "<lastmod>2026-01-15</lastmod>" in xml
        assert "<priority>0.8</priority>" in xml

    def test_to_xml_escapes_special_characters(self) -> None:
        url = SitemapURL(loc="https://example.com/?a=1&b=2")
        xml = url.to_xml()
        assert "&amp;" in xml
        assert "a=1&b=2" not in xml


class TestGenerateSitemap:
    def test_single_url_produces_valid_xml(self) -> None:
        xml = generate_sitemap([SitemapURL(loc="https://example.com/")])
        assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert "<urlset" in xml
        assert "https://example.com/" in xml
        assert xml.count("<url>") == 1

    def test_empty_list_raises(self) -> None:
        with pytest.raises(SitemapValidationError):
            generate_sitemap([])

    def test_exceeding_limit_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Lower the module-level limit rather than constructing 50,001 objects.
        import scripts.sitemap_generator as sg

        monkeypatch.setattr(sg, "MAX_URLS_PER_SITEMAP", 2)
        urls = [SitemapURL(loc=f"https://example.com/{i}") for i in range(3)]
        with pytest.raises(SitemapValidationError):
            sg.generate_sitemap(urls)


class TestGenerateSitemaps:
    def test_splits_into_chunks(self) -> None:
        urls = [SitemapURL(loc=f"https://example.com/{i}") for i in range(5)]
        sitemaps = generate_sitemaps(urls, chunk_size=2)
        assert len(sitemaps) == 3
        assert sitemaps[0].count("<url>") == 2
        assert sitemaps[-1].count("<url>") == 1

    def test_empty_list_raises(self) -> None:
        with pytest.raises(SitemapValidationError):
            generate_sitemaps([])

    def test_chunk_size_exceeding_protocol_limit_raises(self) -> None:
        with pytest.raises(SitemapValidationError):
            generate_sitemaps([SitemapURL(loc="https://example.com/")], chunk_size=MAX_URLS_PER_SITEMAP + 1)


class TestGenerateSitemapIndex:
    def test_valid_index(self) -> None:
        xml = generate_sitemap_index(
            ["https://example.com/sitemap-1.xml", "https://example.com/sitemap-2.xml"]
        )
        assert "<sitemapindex" in xml
        assert xml.count("<sitemap>") == 2

    def test_empty_list_raises(self) -> None:
        with pytest.raises(SitemapValidationError):
            generate_sitemap_index([])
