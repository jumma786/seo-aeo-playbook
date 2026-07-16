"""FastAPI application entry point for the seo-aeo-playbook toolkit.

Run locally with:

    uvicorn api.app:app --reload

This API has no authentication and is intended for local/trusted use
alongside the ``seo-playbook`` CLI, not as a public multi-tenant service —
see ``api/routes.py`` for the SSRF/trust-boundary notes on individual
endpoints.
"""

from __future__ import annotations

from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="seo-aeo-playbook API",
    description="HTTP interface over the seo-aeo-playbook scripts/ toolkit — SEO, AEO, and GEO automation.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def health() -> dict:
    """Liveness check."""
    return {"status": "ok"}
