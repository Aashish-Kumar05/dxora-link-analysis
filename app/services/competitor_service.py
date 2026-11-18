import logging
from typing import Dict, Any, List


class CompetitorService:
    """
    Dedicated competitor intelligence helper for supplementary
    categorization or deep-dive domain comparisons.
    """

    @staticmethod
    def enrich_competitor_comparison(
        brand_name: str,
        category: str,
        raw_competitors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ensures consistent schema and provides structured benchmark comparison.
        """
        enriched = []
        for comp in raw_competitors:
            enriched.append({
                "brand_name": comp.get("name", "Competitor"),
                "main_service": comp.get("main_service", f"{category} Solutions"),
                "target_market": comp.get("target_market", "General Market"),
                "key_strength": comp.get("key_strength", "Market Experience"),
                "weakness_or_gap": comp.get("weakness_or_gap", "Slower Innovation / Higher Cost"),
            })
        return enriched
