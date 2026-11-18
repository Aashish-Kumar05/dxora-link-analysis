import logging
from typing import Dict, Any
from app.services.website_extractor import WebsiteExtractor
from app.services.llm_service import LLMService
from app.schemas import LinkAnalysisResponse

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self):
        self.extractor = WebsiteExtractor()
        self.llm_service = LLMService()

    async def analyze_url(self, url: str) -> LinkAnalysisResponse:
        """
        Orchestrates website extraction, LLM processing, validation,
        and returns the structured 5-section response.
        """
        # 1. Fetch website HTML
        logger.info(f"Fetching website HTML for: {url}")
        html_content = await self.extractor.fetch_html(url)

        # 2. Extract and structure content
        extracted_data = self.extractor.extract_structured_content(html_content, url)
        logger.info(f"Extracted {extracted_data['total_extracted_chars']} chars from {url}")

        # 3. LLM analysis
        analysis_dict, model_used = await self.llm_service.analyze_content(extracted_data)

        # 4. Synthesize final response
        response_payload = {
            "success": True,
            "website": url,
            "brand": analysis_dict.get("brand", {}),
            "analysis": analysis_dict.get("analysis", {}),
            "model_used": model_used,
            "extraction_meta": {
                "title": extracted_data.get("title"),
                "headings_found": {
                    "h1_count": len(extracted_data.get("headings", {}).get("h1", [])),
                    "h2_count": len(extracted_data.get("headings", {}).get("h2", [])),
                },
                "total_content_length": extracted_data.get("total_extracted_chars"),
            }
        }

        # 5. Strict Pydantic validation ensures exact schema match
        validated_response = LinkAnalysisResponse(**response_payload)
        return validated_response
