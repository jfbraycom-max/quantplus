"""
QuantEarningsPro -- /learn routes
Mount in app/main.py:
    from app.routers import learn
    app.include_router(learn.router)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.glossary_service import (
    get_all_terms,
    get_by_slug,
    search_terms,
    group_by_category,
)

log = logging.getLogger(__name__)
router = APIRouter(tags=["learn"])
templates = Jinja2Templates(directory="templates")


@router.get("/learn/glossary", response_class=HTMLResponse)
def glossary_page(
    request: Request,
    q: Optional[str] = Query(None),
):
    all_terms = get_all_terms()
    grouped = group_by_category(all_terms)
    return templates.TemplateResponse("learn/glossary.html", {
        "request":       request,
        "grouped_terms": grouped,
        "total_count":   len(all_terms),
        "prefill_query": q or "",
        "page_title":    "Financial Terms Glossary | QuantPlus Learning",
        "meta_desc": (
            "Free financial glossary covering earnings, options, technical indicators, "
            "macro economics, and quantitative metrics -- with plain-English explanations "
            "from QuantEarningsPro."
        ),
    })


@router.get("/learn/glossary/{slug}", response_class=HTMLResponse)
def glossary_term_redirect(slug: str):
    return RedirectResponse(
        url=f"/learn/glossary?q={slug.replace('-', ' ')}",
        status_code=302,
    )


@router.get("/api/glossary/search")
def glossary_search(q: str = Query(..., min_length=2)):
    try:
        results = search_terms(q)
        if not results:
            return JSONResponse({"found": False, "query": q, "terms": []})
        return JSONResponse({"found": True, "query": q, "count": len(results), "terms": results})
    except Exception as e:
        log.error(f"Glossary search error for '{q}': {e}")
        return JSONResponse({"found": False, "query": q, "error": "Search temporarily unavailable"}, status_code=500)


@router.get("/api/glossary/all")
def glossary_all():
    try:
        terms = get_all_terms()
        return JSONResponse({"terms": terms, "count": len(terms)})
    except Exception as e:
        log.error(f"Glossary all error: {e}")
        return JSONResponse({"terms": [], "count": 0}, status_code=500)
