"""Pydantic request/response models for the seo-aeo-playbook API.

Mirrors the JSON shapes already used by the ``seo-playbook`` CLI
(``cli/commands.py``) so the two interfaces stay consistent. A few
endpoints deliberately diverge from a literal 1:1 CLI mapping for safety:
commands that write files to a server-chosen directory
(``location-pages``, ``service-pages``) or read an arbitrary directory
path (``generate-toc``, ``generate-readme``) instead return/accept content
directly in the request/response body, avoiding server-side arbitrary
file writes or path traversal. This API has no authentication and is
intended for local/trusted use behind your own process boundary, not as
a public multi-tenant service.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------
# Schema
# --------------------------------------------------------------------------


class ArticleSchemaRequest(BaseModel):
    headline: str
    author_name: str
    date_published: str
    date_modified: str | None = None
    author_url: str | None = None
    image: str | None = None
    publisher_name: str | None = None
    publisher_logo: str | None = None
    article_type: str = "Article"


class FaqPair(BaseModel):
    question: str
    answer: str


class FaqSchemaRequest(BaseModel):
    pairs: list[FaqPair] = Field(min_length=1)


class SchemaResponse(BaseModel):
    schema_: dict = Field(alias="schema")
    script_tag: str

    model_config = {"populate_by_name": True}


class SchemaValidateRequest(BaseModel):
    schema_: dict | None = Field(default=None, alias="schema")
    html: str | None = None

    model_config = {"populate_by_name": True}


class ValidationIssueModel(BaseModel):
    severity: str
    path: str
    message: str


class SchemaValidateResponse(BaseModel):
    results: list[list[ValidationIssueModel]]
    has_errors: bool


# --------------------------------------------------------------------------
# Audits
# --------------------------------------------------------------------------


class UrlAuditRequest(BaseModel):
    url: str
    timeout: float = 10.0


class SeoAuditResponse(BaseModel):
    url: str
    score: float
    word_count: int
    title: str | None
    meta_description: str | None
    h1_count: int
    images_missing_alt: int
    internal_link_count: int
    external_link_count: int
    has_canonical: bool
    is_noindex: bool
    issues: list[dict]


class PageSpeedResponse(BaseModel):
    url: str
    score: float
    html_size_bytes: int
    ttfb_seconds: float | None
    render_blocking_scripts: int
    render_blocking_stylesheets: int
    total_images: int
    images_missing_dimensions: int
    lazy_loaded_images: int
    issues: list[dict]


class SiteAuditRequest(BaseModel):
    urls: list[str] = Field(min_length=1)
    timeout: float = 10.0


class PageAuditResponse(BaseModel):
    url: str
    ok: bool
    fetch_error: str | None
    seo_score: float | None
    performance_score: float | None
    overall_score: float | None
    has_schema_errors: bool


class SiteAuditResponse(BaseModel):
    pages: list[PageAuditResponse]
    total_pages: int
    pages_ok: int
    pages_failed: int
    average_seo_score: float | None
    average_performance_score: float | None
    pages_with_schema_errors: list[str]


class LinkCheckRequest(BaseModel):
    urls: list[str] | None = None
    html: str | None = None
    base_url: str = ""
    timeout: float = 10.0


class LinkCheckResultModel(BaseModel):
    url: str
    status_code: int | None
    final_url: str | None
    redirected: bool
    error: str | None
    is_broken: bool


class LinkCheckResponse(BaseModel):
    results: list[LinkCheckResultModel]
    broken_count: int


# --------------------------------------------------------------------------
# Sitemaps, robots.txt, llms.txt
# --------------------------------------------------------------------------


class SitemapUrlModel(BaseModel):
    loc: str
    lastmod: str | None = None
    changefreq: str | None = None
    priority: float | None = None


class SitemapRequest(BaseModel):
    urls: list[SitemapUrlModel] = Field(min_length=1)


class RobotsGroupModel(BaseModel):
    user_agent: str = "*"
    disallow: list[str] = Field(default_factory=list)
    allow: list[str] = Field(default_factory=list)
    crawl_delay: float | None = None


class RobotsRequest(BaseModel):
    groups: list[RobotsGroupModel] = Field(min_length=1)
    sitemap_urls: list[str] | None = None


class LlmsTxtLinkModel(BaseModel):
    title: str
    url: str
    description: str | None = None


class LlmsTxtSectionModel(BaseModel):
    heading: str
    links: list[LlmsTxtLinkModel] = Field(min_length=1)


class LlmsGenerateRequest(BaseModel):
    name: str
    summary: str
    sections: list[LlmsTxtSectionModel] = Field(min_length=1)


class CrawlerAuditRequest(BaseModel):
    robots_txt: str


class CrawlerStatusModel(BaseModel):
    crawler: str
    purpose: str
    allowed: bool
    blocked_by: str | None
    warning: str | None


class CrawlerAuditResponse(BaseModel):
    statuses: list[CrawlerStatusModel]
    blocked_count: int


# --------------------------------------------------------------------------
# Keywords
# --------------------------------------------------------------------------


class KeywordClusterRequest(BaseModel):
    keywords: list[str] = Field(min_length=1)
    threshold: float | None = None


class KeywordClusterModel(BaseModel):
    label: str
    keywords: list[str]


class KeywordClusterResponse(BaseModel):
    clusters: list[KeywordClusterModel]


class KeywordMappingModel(BaseModel):
    keyword: str
    url: str


class CannibalizationAuditRequest(BaseModel):
    mappings: list[KeywordMappingModel] = Field(min_length=1)


class CannibalizationIssueModel(BaseModel):
    keyword: str
    urls: list[str]


class CannibalizationAuditResponse(BaseModel):
    issues: list[CannibalizationIssueModel]


class KeywordMapSuggestRequest(BaseModel):
    keywords: list[str] = Field(min_length=1)
    pages: dict[str, str] = Field(min_length=1)
    threshold: float | None = None


class KeywordMapSuggestResponse(BaseModel):
    mappings: list[KeywordMappingModel]
    unmapped: list[str]


# --------------------------------------------------------------------------
# Entities & internal linking
# --------------------------------------------------------------------------


class EntityExtractRequest(BaseModel):
    text: str
    compare_text: str | None = None


class EntityMentionModel(BaseModel):
    text: str
    entity_type: str
    count: int
    salience: float


class EntityExtractResponse(BaseModel):
    mentions: list[EntityMentionModel]
    gaps: list[str] = Field(default_factory=list)


class LinkSuggestPageModel(BaseModel):
    url: str
    title: str
    body: str = ""
    keywords: list[str] = Field(default_factory=list)
    links_to: list[str] = Field(default_factory=list)


class LinkSuggestRequest(BaseModel):
    pages: list[LinkSuggestPageModel] = Field(min_length=1)
    max_per_page: int = 5


class LinkSuggestionModel(BaseModel):
    source_url: str
    target_url: str
    anchor_text: str


class LinkSuggestResponse(BaseModel):
    suggestions: list[LinkSuggestionModel]
    orphan_pages: list[str]


# --------------------------------------------------------------------------
# GEO
# --------------------------------------------------------------------------


class GeoScoreRequest(BaseModel):
    text: str


class PassageScoreModel(BaseModel):
    text: str
    word_count: int
    self_contained: bool
    has_specific_fact: bool
    has_structural_label: bool
    score: float
    issues: list[str]


class GeoScoreResponse(BaseModel):
    passages: list[PassageScoreModel]
    average_score: float


# --------------------------------------------------------------------------
# Content generation
# --------------------------------------------------------------------------


class MetaRequest(BaseModel):
    title: str | None = None
    brand: str | None = None
    description: str | None = None


class MetaResponse(BaseModel):
    title: str | None = None
    title_warnings: list[str] = Field(default_factory=list)
    description: str | None = None
    description_warnings: list[str] = Field(default_factory=list)


class ContentBriefRequest(BaseModel):
    primary_keyword: str
    related_keywords: list[str] = Field(default_factory=list)
    target_word_count: int = 1500
    questions: list[str] | None = None
    entities: list[str] | None = None


class BriefSectionModel(BaseModel):
    heading: str
    keywords: list[str]
    target_word_count: int


class ContentBriefResponse(BaseModel):
    primary_keyword: str
    target_word_count: int
    sections: list[BriefSectionModel]
    questions_to_answer: list[str]
    entities_to_mention: list[str]
    markdown: str


class FaqGenerateRequest(BaseModel):
    items: list[FaqPair] = Field(min_length=1)


class FaqGenerateResponse(BaseModel):
    markdown: str
    schema_tag: str
    issues: list[str]


class BlogScaffoldRequest(BaseModel):
    title: str
    slug: str
    author_name: str
    date_published: str
    primary_keyword: str
    related_keywords: list[str] = Field(default_factory=list)
    target_word_count: int = 1500
    questions: list[str] | None = None


class BlogScaffoldResponse(BaseModel):
    markdown: str


# --------------------------------------------------------------------------
# Local SEO page generators
# --------------------------------------------------------------------------


class NapModel(BaseModel):
    name: str
    street_address: str
    address_locality: str
    address_region: str
    postal_code: str
    telephone: str
    address_country: str = "US"


class LocationPageSpecModel(BaseModel):
    url_slug: str
    nap: NapModel
    hours: dict[str, str] = Field(default_factory=dict)
    unique_content: str = ""
    business_type: str = "LocalBusiness"


class LocationPagesRequest(BaseModel):
    specs: list[LocationPageSpecModel] = Field(min_length=1)
    skip_quality_gates: bool = False


class ServicePageSpecModel(BaseModel):
    url_slug: str
    business_name: str
    service_name: str
    area_served: str
    telephone: str
    unique_content: str = ""
    price_range: str | None = None


class ServicePagesRequest(BaseModel):
    specs: list[ServicePageSpecModel] = Field(min_length=1)
    skip_quality_gates: bool = False


class RenderedPagesResponse(BaseModel):
    pages: dict[str, str]


# --------------------------------------------------------------------------
# Documentation tooling
# --------------------------------------------------------------------------


class ChapterInputModel(BaseModel):
    filename: str
    content: str


class TocRequest(BaseModel):
    chapters: list[ChapterInputModel] = Field(min_length=1)


class TocResponse(BaseModel):
    table: str


class RelatedBookModel(BaseModel):
    title: str
    path: str
    description: str


class ReadmeRequest(BaseModel):
    title: str
    description: str
    chapters: list[ChapterInputModel] = Field(min_length=1)
    related_books: list[RelatedBookModel] = Field(default_factory=list)
    license_path: str = "../../../../LICENSE"


class ReadmeResponse(BaseModel):
    readme: str
