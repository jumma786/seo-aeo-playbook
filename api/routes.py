"""API routes wiring the seo-aeo-playbook toolkit up over HTTP.

Each route is a thin adapter over the same ``scripts/`` functions the
``seo-playbook`` CLI wraps (``cli/commands.py``) — this module owns
request/response translation and error mapping, while the actual SEO
logic stays in the already-tested ``scripts`` modules.

Endpoints that fetch a client-supplied URL (``/audit/*``, ``/links/check``)
make outbound HTTP requests from wherever this API runs, the same as the
CLI does locally — be mindful of SSRF exposure if this is ever deployed
somewhere less trusted than a local/internal environment.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.models import (
    ArticleSchemaRequest,
    BlogScaffoldRequest,
    BlogScaffoldResponse,
    CannibalizationAuditRequest,
    CannibalizationAuditResponse,
    ContentBriefRequest,
    ContentBriefResponse,
    CrawlerAuditRequest,
    CrawlerAuditResponse,
    EntityExtractRequest,
    EntityExtractResponse,
    FaqGenerateRequest,
    FaqGenerateResponse,
    FaqSchemaRequest,
    KeywordClusterRequest,
    KeywordClusterResponse,
    KeywordMapSuggestRequest,
    KeywordMapSuggestResponse,
    LinkCheckRequest,
    LinkCheckResponse,
    LinkSuggestRequest,
    LinkSuggestResponse,
    LocationPagesRequest,
    MetaRequest,
    MetaResponse,
    ReadmeRequest,
    ReadmeResponse,
    RenderedPagesResponse,
    RobotsRequest,
    SchemaResponse,
    SchemaValidateRequest,
    SchemaValidateResponse,
    ServicePagesRequest,
    SitemapRequest,
    SiteAuditRequest,
    SiteAuditResponse,
    LlmsGenerateRequest,
    PageAuditResponse,
    PageSpeedResponse,
    SeoAuditResponse,
    TocRequest,
    TocResponse,
    UrlAuditRequest,
)

router = APIRouter()


# --------------------------------------------------------------------------
# Schema
# --------------------------------------------------------------------------


@router.post("/schema/article", response_model=SchemaResponse)
def schema_article(request: ArticleSchemaRequest) -> SchemaResponse:
    from scripts.schema_generator import SchemaValidationError, generate_article_schema, to_script_tag

    try:
        schema = generate_article_schema(**request.model_dump())
    except SchemaValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SchemaResponse(schema=schema, script_tag=to_script_tag(schema))


@router.post("/schema/faq", response_model=SchemaResponse)
def schema_faq(request: FaqSchemaRequest) -> SchemaResponse:
    from scripts.schema_generator import SchemaValidationError, generate_faq_schema, to_script_tag

    pairs = [(pair.question, pair.answer) for pair in request.pairs]
    try:
        schema = generate_faq_schema(pairs)
    except SchemaValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SchemaResponse(schema=schema, script_tag=to_script_tag(schema))


@router.post("/schema/validate", response_model=SchemaValidateResponse)
def schema_validate(request: SchemaValidateRequest) -> SchemaValidateResponse:
    from scripts.schema_validator import has_errors, validate_html, validate_schema

    if request.html is not None:
        results = [issues for _, issues in validate_html(request.html)]
    elif request.schema_ is not None:
        results = [validate_schema(request.schema_)]
    else:
        raise HTTPException(status_code=400, detail="Provide either 'schema' or 'html'")

    return SchemaValidateResponse(
        results=[[issue.__dict__ for issue in issues] for issues in results],
        has_errors=any(has_errors(issues) for issues in results),
    )


# --------------------------------------------------------------------------
# Audits
# --------------------------------------------------------------------------


@router.post("/audit/seo", response_model=SeoAuditResponse)
def audit_seo(request: UrlAuditRequest) -> SeoAuditResponse:
    from scripts.seo_audit import audit_url

    try:
        result = audit_url(request.url, timeout=request.timeout)
    except Exception as exc:  # noqa: BLE001 - surface any fetch failure to the API client
        raise HTTPException(status_code=502, detail=f"Failed to audit {request.url}: {exc}") from exc

    return SeoAuditResponse(
        url=result.url,
        score=result.score,
        word_count=result.word_count,
        title=result.title,
        meta_description=result.meta_description,
        h1_count=result.h1_count,
        images_missing_alt=result.images_missing_alt,
        internal_link_count=result.internal_link_count,
        external_link_count=result.external_link_count,
        has_canonical=result.has_canonical,
        is_noindex=result.is_noindex,
        issues=[issue.__dict__ for issue in result.issues],
    )


@router.post("/audit/page-speed", response_model=PageSpeedResponse)
def audit_page_speed(request: UrlAuditRequest) -> PageSpeedResponse:
    from scripts.page_speed import audit_url_performance

    try:
        result = audit_url_performance(request.url, timeout=request.timeout)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Failed to audit {request.url}: {exc}") from exc

    return PageSpeedResponse(
        url=result.url,
        score=result.score,
        html_size_bytes=result.html_size_bytes,
        ttfb_seconds=result.ttfb_seconds,
        render_blocking_scripts=result.render_blocking_scripts,
        render_blocking_stylesheets=result.render_blocking_stylesheets,
        total_images=result.total_images,
        images_missing_dimensions=result.images_missing_dimensions,
        lazy_loaded_images=result.lazy_loaded_images,
        issues=[issue.__dict__ for issue in result.issues],
    )


@router.post("/audit/site", response_model=SiteAuditResponse)
def audit_site_endpoint(request: SiteAuditRequest) -> SiteAuditResponse:
    from scripts.site_audit import audit_site, summarize_site

    results = audit_site(request.urls, timeout=request.timeout)
    summary = summarize_site(results)

    return SiteAuditResponse(
        pages=[
            PageAuditResponse(
                url=result.url,
                ok=result.ok,
                fetch_error=result.fetch_error,
                seo_score=result.seo.score if result.seo else None,
                performance_score=result.performance.score if result.performance else None,
                overall_score=result.overall_score,
                has_schema_errors=result.has_schema_errors,
            )
            for result in results
        ],
        total_pages=summary.total_pages,
        pages_ok=summary.pages_ok,
        pages_failed=summary.pages_failed,
        average_seo_score=summary.average_seo_score,
        average_performance_score=summary.average_performance_score,
        pages_with_schema_errors=summary.pages_with_schema_errors,
    )


@router.post("/audit/links", response_model=LinkCheckResponse)
def audit_links(request: LinkCheckRequest) -> LinkCheckResponse:
    from scripts.link_checker import check_links, extract_links_from_html

    if request.html is not None:
        urls = extract_links_from_html(request.html, base_url=request.base_url)
    elif request.urls:
        urls = request.urls
    else:
        raise HTTPException(status_code=400, detail="Provide either 'urls' or 'html'")

    results = check_links(urls, timeout=request.timeout)
    return LinkCheckResponse(
        results=[
            {
                "url": r.url,
                "status_code": r.status_code,
                "final_url": r.final_url,
                "redirected": r.redirected,
                "error": r.error,
                "is_broken": r.is_broken,
            }
            for r in results
        ],
        broken_count=sum(1 for r in results if r.is_broken),
    )


# --------------------------------------------------------------------------
# Sitemaps, robots.txt, llms.txt
# --------------------------------------------------------------------------


@router.post("/sitemap")
def sitemap_endpoint(request: SitemapRequest) -> dict:
    from scripts.sitemap_generator import SitemapURL, SitemapValidationError, generate_sitemap

    try:
        urls = [SitemapURL(**item.model_dump()) for item in request.urls]
        xml = generate_sitemap(urls)
    except SitemapValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"xml": xml}


@router.post("/robots")
def robots_endpoint(request: RobotsRequest) -> dict:
    from scripts.robots_generator import RobotsGroup, RobotsValidationError, generate_robots_txt

    try:
        groups = [RobotsGroup(**group.model_dump()) for group in request.groups]
        content = generate_robots_txt(groups, sitemap_urls=request.sitemap_urls)
    except RobotsValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"content": content}


@router.post("/llms/generate")
def llms_generate_endpoint(request: LlmsGenerateRequest) -> dict:
    from scripts.llms_txt_generator import LlmsTxtValidationError, sections_from_dict
    from scripts.llms_txt_generator import generate_llms_txt as build_llms_txt

    try:
        sections = sections_from_dict([section.model_dump() for section in request.sections])
        content = build_llms_txt(request.name, request.summary, sections)
    except LlmsTxtValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"content": content}


@router.post("/llms/audit-crawlers", response_model=CrawlerAuditResponse)
def llms_audit_crawlers_endpoint(request: CrawlerAuditRequest) -> CrawlerAuditResponse:
    from scripts.llms_validator import audit_robots_txt

    statuses = audit_robots_txt(request.robots_txt)
    return CrawlerAuditResponse(
        statuses=[status.__dict__ for status in statuses],
        blocked_count=sum(1 for status in statuses if not status.allowed),
    )


# --------------------------------------------------------------------------
# Keywords
# --------------------------------------------------------------------------


@router.post("/keywords/cluster", response_model=KeywordClusterResponse)
def keywords_cluster(request: KeywordClusterRequest) -> KeywordClusterResponse:
    from scripts.keyword_cluster import DEFAULT_SIMILARITY_THRESHOLD, cluster_keywords

    threshold = request.threshold if request.threshold is not None else DEFAULT_SIMILARITY_THRESHOLD
    try:
        clusters = cluster_keywords(request.keywords, similarity_threshold=threshold)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return KeywordClusterResponse(
        clusters=[{"label": c.label, "keywords": c.keywords} for c in clusters]
    )


@router.post("/keywords/map/audit", response_model=CannibalizationAuditResponse)
def keywords_map_audit(request: CannibalizationAuditRequest) -> CannibalizationAuditResponse:
    from scripts.keyword_mapper import KeywordMapping, find_cannibalization

    mappings = [KeywordMapping(keyword=m.keyword, url=m.url) for m in request.mappings]
    issues = find_cannibalization(mappings)
    return CannibalizationAuditResponse(issues=[{"keyword": i.keyword, "urls": i.urls} for i in issues])


@router.post("/keywords/map/suggest", response_model=KeywordMapSuggestResponse)
def keywords_map_suggest(request: KeywordMapSuggestRequest) -> KeywordMapSuggestResponse:
    from scripts.keyword_mapper import DEFAULT_MATCH_THRESHOLD, map_keywords_to_urls, unmapped_keywords

    threshold = request.threshold if request.threshold is not None else DEFAULT_MATCH_THRESHOLD
    mappings = map_keywords_to_urls(request.keywords, request.pages, threshold=threshold)
    return KeywordMapSuggestResponse(
        mappings=[{"keyword": m.keyword, "url": m.url} for m in mappings],
        unmapped=unmapped_keywords(request.keywords, mappings),
    )


# --------------------------------------------------------------------------
# Entities & internal linking
# --------------------------------------------------------------------------


@router.post("/entities/extract", response_model=EntityExtractResponse)
def entities_extract(request: EntityExtractRequest) -> EntityExtractResponse:
    from scripts.entity_extractor import compute_salience, extract_entities, find_entity_gaps

    mentions = extract_entities(request.text)
    salience = compute_salience(mentions)
    gaps: list[str] = []
    if request.compare_text is not None:
        competitor_mentions = extract_entities(request.compare_text)
        gaps = find_entity_gaps(mentions, competitor_mentions)

    return EntityExtractResponse(
        mentions=[
            {"text": m.text, "entity_type": m.entity_type, "count": m.count, "salience": salience[m.text]}
            for m in mentions
        ],
        gaps=gaps,
    )


@router.post("/links/suggest", response_model=LinkSuggestResponse)
def links_suggest(request: LinkSuggestRequest) -> LinkSuggestResponse:
    from scripts.internal_linker import Page, find_orphan_pages, suggest_internal_links

    pages = [
        Page(url=p.url, title=p.title, body=p.body, keywords=p.keywords, links_to=set(p.links_to))
        for p in request.pages
    ]
    suggestions = suggest_internal_links(pages, max_suggestions_per_page=request.max_per_page)
    return LinkSuggestResponse(
        suggestions=[
            {"source_url": s.source_url, "target_url": s.target_url, "anchor_text": s.anchor_text}
            for s in suggestions
        ],
        orphan_pages=find_orphan_pages(pages),
    )


# --------------------------------------------------------------------------
# Content generation
# --------------------------------------------------------------------------


@router.post("/meta", response_model=MetaResponse)
def meta_endpoint(request: MetaRequest) -> MetaResponse:
    from scripts.meta_generator import (
        generate_meta_description,
        generate_title,
        validate_meta_description,
        validate_title,
    )

    if not request.title and not request.description:
        raise HTTPException(status_code=400, detail="Provide 'title' and/or 'description'")

    response = MetaResponse()
    if request.title:
        response.title = generate_title(request.title, brand=request.brand)
        response.title_warnings = validate_title(response.title)
    if request.description:
        response.description = generate_meta_description(request.description)
        response.description_warnings = validate_meta_description(response.description)
    return response


@router.post("/content-brief", response_model=ContentBriefResponse)
def content_brief_endpoint(request: ContentBriefRequest) -> ContentBriefResponse:
    from scripts.content_brief import format_brief, generate_content_brief

    try:
        brief = generate_content_brief(
            request.primary_keyword,
            request.related_keywords,
            target_word_count=request.target_word_count,
            questions=request.questions,
            entities=request.entities,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ContentBriefResponse(
        primary_keyword=brief.primary_keyword,
        target_word_count=brief.target_word_count,
        sections=[
            {"heading": s.heading, "keywords": s.keywords, "target_word_count": s.target_word_count}
            for s in brief.sections
        ],
        questions_to_answer=brief.questions_to_answer,
        entities_to_mention=brief.entities_to_mention,
        markdown=format_brief(brief),
    )


@router.post("/faq", response_model=FaqGenerateResponse)
def faq_endpoint(request: FaqGenerateRequest) -> FaqGenerateResponse:
    from scripts.faq_generator import (
        FaqItem,
        format_validation_report,
        generate_faq_markdown,
        generate_faq_schema_tag,
        validate_faq_items,
    )

    items = [FaqItem(question=item.question, answer=item.answer) for item in request.items]
    issues = validate_faq_items(items)
    return FaqGenerateResponse(
        markdown=generate_faq_markdown(items),
        schema_tag=generate_faq_schema_tag(items),
        issues=[format_validation_report([issue]) for issue in issues] if issues else [],
    )


@router.post("/blog-scaffold", response_model=BlogScaffoldResponse)
def blog_scaffold_endpoint(request: BlogScaffoldRequest) -> BlogScaffoldResponse:
    from scripts.blog_generator import BlogPostSpec, generate_blog_scaffold
    from scripts.content_brief import generate_content_brief

    try:
        brief = generate_content_brief(
            request.primary_keyword,
            request.related_keywords,
            target_word_count=request.target_word_count,
            questions=request.questions,
        )
        spec = BlogPostSpec(
            title=request.title,
            slug=request.slug,
            author_name=request.author_name,
            date_published=request.date_published,
            brief=brief,
        )
        markdown = generate_blog_scaffold(spec)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BlogScaffoldResponse(markdown=markdown)


# --------------------------------------------------------------------------
# Local SEO page generators
# --------------------------------------------------------------------------


@router.post("/local/location-pages", response_model=RenderedPagesResponse)
def location_pages_endpoint(request: LocationPagesRequest) -> RenderedPagesResponse:
    from scripts.location_page_generator import NAP, LocationPageQualityError, LocationPageSpec, generate_location_pages

    specs = [
        LocationPageSpec(
            url_slug=s.url_slug,
            nap=NAP(**s.nap.model_dump()),
            hours=s.hours,
            unique_content=s.unique_content,
            business_type=s.business_type,
        )
        for s in request.specs
    ]
    try:
        pages = generate_location_pages(specs, enforce_quality_gates=not request.skip_quality_gates)
    except LocationPageQualityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RenderedPagesResponse(pages=pages)


@router.post("/local/service-pages", response_model=RenderedPagesResponse)
def service_pages_endpoint(request: ServicePagesRequest) -> RenderedPagesResponse:
    from scripts.service_page_generator import ServiceAreaPageSpec, ServicePageQualityError, generate_service_pages

    specs = [ServiceAreaPageSpec(**s.model_dump()) for s in request.specs]
    try:
        pages = generate_service_pages(specs, enforce_quality_gates=not request.skip_quality_gates)
    except ServicePageQualityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RenderedPagesResponse(pages=pages)


# --------------------------------------------------------------------------
# Documentation tooling
# --------------------------------------------------------------------------


@router.post("/book-docs/toc", response_model=TocResponse)
def docs_toc_endpoint(request: TocRequest) -> TocResponse:
    from scripts.generate_toc import ChapterParseError, generate_toc_table, parse_chapter

    try:
        chapters = [parse_chapter(c.content, filename=c.filename) for c in request.chapters]
        table = generate_toc_table(chapters)
    except (ChapterParseError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TocResponse(table=table)


@router.post("/book-docs/readme", response_model=ReadmeResponse)
def docs_readme_endpoint(request: ReadmeRequest) -> ReadmeResponse:
    from scripts.generate_readme import RelatedBook, compose_readme
    from scripts.generate_toc import ChapterParseError, generate_toc_table, parse_chapter

    try:
        chapters = [parse_chapter(c.content, filename=c.filename) for c in request.chapters]
        toc = generate_toc_table(chapters)
        related_books = [RelatedBook(**book.model_dump()) for book in request.related_books]
        readme = compose_readme(
            request.title, request.description, toc, related_books=related_books, license_path=request.license_path
        )
    except (ChapterParseError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ReadmeResponse(readme=readme)
