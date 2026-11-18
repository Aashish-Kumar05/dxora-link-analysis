from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class LinkAnalysisRequest(BaseModel):
    url: str = Field(
        ...,
        description="The website URL to analyze (e.g., https://example.com)",
        examples=["https://example.com"]
    )


class BrandInfo(BaseModel):
    name: str = Field(..., description="Brand name identified from the website")
    category: str = Field(..., description="Main business or industry category")
    summary: str = Field(..., description="Brief summary of the business and value proposition")


class CompetitorDetail(BaseModel):
    name: str = Field(..., description="Competitor brand name")
    main_service: str = Field(..., description="Competitor's primary service or offering")
    target_market: str = Field(..., description="Primary market or customer profile of the competitor")
    key_strength: str = Field(..., description="Key strength of this competitor")
    weakness_or_gap: str = Field(..., description="Identified competitor weakness or market gap")


class CompetitorAnalysis(BaseModel):
    brand_overview: str = Field(..., description="Detailed overview of the client brand")
    main_category: str = Field(..., description="Primary business industry/category")
    main_products_services: List[str] = Field(default_factory=list, description="Primary products and services offered")
    competitors: List[CompetitorDetail] = Field(
        ...,
        min_length=3,
        description="Minimum 3 identified competitors with comparative breakdown"
    )
    strengths: List[str] = Field(default_factory=list, description="Brand's competitive advantages")
    opportunities: List[str] = Field(default_factory=list, description="Opportunities to improve market positioning")
    data_source_note: str = Field(
        default="AI-generated competitor market intelligence based on domain category and public web knowledge",
        description="Note regarding competitor data origin"
    )


class TargetSearchQuery(BaseModel):
    query: str = Field(..., description="Target search query")
    platforms: List[str] = Field(..., description="Platforms where query is relevant (Google, Facebook, Instagram, LinkedIn, X)")
    intent: str = Field(..., description="Search intent (e.g. Service Search, Business Discovery, Inspiration, B2B Search)")
    business_relevance: str = Field(..., description="How this query directly aligns with business goals")
    target_audience: str = Field(..., description="Audience demographic or persona searching for this query")


class SEOImprovements(BaseModel):
    primary_keyword: str = Field(..., description="Recommended primary keyword")
    secondary_keywords: List[str] = Field(default_factory=list, description="Recommended secondary keywords")
    long_tail_keywords: List[str] = Field(default_factory=list, description="Recommended long-tail keywords")
    recommended_title: str = Field(..., description="Recommended SEO title tag (under 60 chars)")
    meta_description: str = Field(..., description="Recommended meta description (under 160 chars)")
    supporting_content: List[str] = Field(default_factory=list, description="Suggested landing pages, FAQs, blog topics, or guides")


class TopService(BaseModel):
    service_name: str = Field(..., description="Name of the service")
    description: str = Field(..., description="Short explanation of what the service delivers")
    target_industry: str = Field(..., description="Relevant business vertical or industry")
    target_customer: str = Field(..., description="Specific potential customer type (e.g., Enterprise, SMB, Startups)")
    main_benefit: str = Field(..., description="Why customers need and choose this service")
    source: str = Field(
        default="Extracted from website content",
        description="Source of the service identification ('Extracted from website content' or 'Inferred recommendation')"
    )


class TargetAudienceSegment(BaseModel):
    audience: str = Field(..., description="Name/Label of the audience segment (e.g. Audience 1, Small Businesses)")
    business_type: str = Field(..., description="Business size/type (e.g. Startups, Retail, Enterprise)")
    requirement: str = Field(..., description="Key requirement, core need, or problem solved")


class TargetAudience(BaseModel):
    primary_audience: List[str] = Field(default_factory=list, description="Primary customer demographics / buyer personas")
    secondary_audience: List[str] = Field(default_factory=list, description="Secondary or indirect audiences")
    industries: List[str] = Field(default_factory=list, description="Key target industry segments")
    customer_needs: List[str] = Field(default_factory=list, description="Core customer pain points and challenges")
    potential_interests: List[str] = Field(default_factory=list, description="Customer interests and affinities")
    geographical_focus: Optional[str] = Field(None, description="Geographical/location focus if indicated on website")
    audience_segments: List[TargetAudienceSegment] = Field(
        default_factory=list,
        description="Structured audience segments for marketing campaigns"
    )


class AnalysisData(BaseModel):
    competitor_analysis: CompetitorAnalysis
    target_search_queries: List[TargetSearchQuery]
    seo_improvements: SEOImprovements
    top_services: List[TopService]
    target_audience: TargetAudience


class LinkAnalysisResponse(BaseModel):
    success: bool = True
    website: str
    brand: BrandInfo
    analysis: AnalysisData
    model_used: Optional[str] = None
    extraction_meta: Optional[dict] = None
