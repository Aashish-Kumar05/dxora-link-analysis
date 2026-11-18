import re
import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from app.config import settings


class WebsiteExtractor:
    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def fetch_html(self, url: str) -> str:
        """
        Fetches website HTML asynchronously with timeouts, follow_redirects,
        and standard error handling.
        """
        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
                verify=False,  # tolerate self-signed or minor cert anomalies in dev/test
            ) as client:
                response = await client.get(url)
                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Unable to access website '{url}'. HTTP status code {response.status_code}."
                    )
                return response.text
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Request to website '{url}' timed out after {self.timeout} seconds."
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to connect to website '{url}': {str(e)}"
            )

    def extract_structured_content(self, html: str, url: str) -> dict:
        """
        Extracts metadata, headers, structured paragraphs, navigation links,
        and cleans boilerplate/scripts/CSS to minimize LLM token waste.
        """
        soup = BeautifulSoup(html, "html.parser")

        # 1. Remove non-content elements
        for element in soup(["script", "style", "noscript", "svg", "iframe", "footer", "form", "select", "button"]):
            element.decompose()

        # 2. Extract Metadata
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        
        meta_desc = ""
        meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)}) or \
                        soup.find("meta", attrs={"property": re.compile(r"^og:description$", re.I)})
        if meta_desc_tag and meta_desc_tag.get("content"):
            meta_desc = meta_desc_tag["content"].strip()

        og_title_tag = soup.find("meta", attrs={"property": re.compile(r"^og:title$", re.I)})
        og_title = og_title_tag["content"].strip() if og_title_tag and og_title_tag.get("content") else ""

        og_site_name_tag = soup.find("meta", attrs={"property": re.compile(r"^og:site_name$", re.I)})
        site_name = og_site_name_tag["content"].strip() if og_site_name_tag and og_site_name_tag.get("content") else ""

        meta_keywords_tag = soup.find("meta", attrs={"name": re.compile(r"^keywords$", re.I)})
        keywords = meta_keywords_tag["content"].strip() if meta_keywords_tag and meta_keywords_tag.get("content") else ""

        # 3. Headings hierarchy
        h1s = [h.get_text(separator=" ", strip=True) for h in soup.find_all("h1")]
        h2s = [h.get_text(separator=" ", strip=True) for h in soup.find_all("h2")][:10]
        h3s = [h.get_text(separator=" ", strip=True) for h in soup.find_all("h3")][:10]

        # 4. Text blocks
        paragraphs = []
        for p in soup.find_all(["p", "li"]):
            text = p.get_text(separator=" ", strip=True)
            if len(text) > 25:  # filter tiny fragments
                paragraphs.append(text)

        # Remove duplicate paragraphs preserving order
        seen = set()
        deduped_paragraphs = []
        for p in paragraphs:
            if p not in seen:
                seen.add(p)
                deduped_paragraphs.append(p)

        combined_text = "\n".join(deduped_paragraphs)
        if len(combined_text) > settings.MAX_CONTENT_LENGTH:
            combined_text = combined_text[:settings.MAX_CONTENT_LENGTH] + "\n...[Content truncated for token optimization]..."

        return {
            "url": url,
            "title": title or og_title,
            "site_name": site_name,
            "meta_description": meta_desc,
            "meta_keywords": keywords,
            "headings": {
                "h1": h1s,
                "h2": h2s,
                "h3": h3s
            },
            "body_excerpt": combined_text,
            "total_extracted_chars": len(combined_text)
        }
