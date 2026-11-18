from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse
from app.utils.validators import validate_and_sanitize_url
from app.services.analysis_service import AnalysisService

app = FastAPI(
    title="AI-Powered Website Link Analysis API",
    description=(
        "Enterprise-grade FastAPI application that extracts website content and leverages "
        "LLMs to generate structured 5-section business, competitor, SEO, search query, and audience intelligence."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analysis_service = AnalysisService()


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "service": "AI-Powered Website Link Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "configured_llm_provider": settings.LLM_PROVIDER,
        "configured_model": settings.GROQ_MODEL if settings.LLM_PROVIDER == "groq" else settings.GEMINI_MODEL
    }



@app.post(
    "/link-analysis",
    response_model=LinkAnalysisResponse,
    status_code=200,
    summary="Analyze website URL and generate comprehensive 5-section intelligence",
    tags=["Analysis"]
)
async def analyze_link(request: LinkAnalysisRequest):
    """
    Analyzes a given website URL:
    - **Validates URL & blocks internal SSRF IP addresses**.
    - **Fetches & cleans DOM content** (removes scripts, styles, boilerplates).
    - **Executes LLM intelligence** across:
      1. Competitor vs Brand Comparison (min 3 competitors, strengths, gaps)
      2. Top 5 Target Search Queries (Google, Facebook, Instagram, LinkedIn, X)
      3. SEO Improvements (Keywords, Title, Meta Description, Supporting Content)
      4. Top 5 Services (Industry, Customer Profile, Benefit, Source)
      5. Target Audience Identification (Segments, Demographics, Needs, Interests)
    """
    # 1. URL validation & SSRF protection
    sanitized_url = validate_and_sanitize_url(request.url)

    # 2. Complete analysis pipeline
    result = await analysis_service.analyze_url(sanitized_url)

    return result
