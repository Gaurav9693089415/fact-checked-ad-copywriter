from typing import List, Optional
from urllib.parse import urlparse
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.utils.scraper import scrape_text_from_url


# --- Helper functions ---

def _domain_of(url: str) -> str:
    """Extract domain name (e.g., 'apple.com')."""
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _extract_possible_brand(claim: str) -> Optional[str]:
    """
    Extracts a likely brand name from the claim text.
    Example: "Apple iPhone 15 has the best camera" → 'apple'
    """
    words = claim.split()
    for w in words:
        if re.match(r"^[A-Z][a-z]+$", w):  # capitalized word → possible brand
            return w.lower()
    return None


def _pick_best_result(results: List[dict], trusted_domains: Optional[List[str]]) -> Optional[str]:
    """Choose best URL, preferring those from trusted/official domains."""
    if not results:
        return None
    trusted_set = {d.lower().replace("www.", "") for d in (trusted_domains or [])}
    for r in results:
        url = r.get("url")
        if not url:
            continue
        dom = _domain_of(url)
        if dom in trusted_set:
            return url
    # fallback: pick first available URL
    for r in results:
        if r.get("url"):
            return r["url"]
    return None


def _generate_search_query(claim: str, llm: ChatOpenAI) -> str:
    """Use LLM to generate a focused web search query for this claim."""
    parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_template(
        "You are a search expert. Produce a short, focused query to verify this factual claim.\n\nClaim: {claim}\n\nReturn only the query."
    )
    chain = prompt | llm | parser
    return chain.invoke({"claim": claim}).strip()


def _verify_with_llm(claim: str, source_text: str, llm: ChatOpenAI) -> Optional[bool]:
    """Ask LLM to verify claim truth using the provided source text."""
    parser = StrOutputParser()
    template = (
        "You are a meticulous fact-checker. Analyze if the Source Text confirms the Claim.\n"
        "Respond only with 'Yes' or 'No'.\n\n"
        "Claim: {claim}\n\nSource Text: {source_text}\n"
    )
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | parser
    try:
        resp = chain.invoke({"claim": claim, "source_text": source_text[:15000]})
    except Exception as e:
        print(f"LLM verification call failed: {e}")
        return None

    r = resp.strip().lower()
    if r.startswith("yes"):
        return True
    if r.startswith("no"):
        return False
    return None


# --- Main verification pipeline ---

def verify_claim(claim: str, product_url: Optional[str] = None) -> Optional[str]:
    """
    Verifies a claim by:
    1. Searching within the official domain first (if identifiable)
    2. Falling back to global web search if needed
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    search_tool = TavilySearchResults(max_results=3)

    def _search_and_verify(query: str, preferred_domains: List[str] = None) -> Optional[str]:
        """Search Tavily and verify claim using retrieved sources."""
        try:
            results = search_tool.invoke(query)
        except Exception as e:
            print(f"Tavily search error: {e}")
            return None

        if not results or not isinstance(results, list):
            return None

        source_url = _pick_best_result(results, preferred_domains)
        if not source_url:
            return None

        scraped_text = scrape_text_from_url(source_url)
        if not scraped_text:
            return None

        verdict = _verify_with_llm(claim, scraped_text, llm)
        if verdict:
            return source_url
        return None

    # --- Step 1: Identify official domain from brand name or product URL ---
    brand_domain = None

    # Try to extract domain from provided product URL
    if product_url:
        brand_domain = _domain_of(product_url)

    # Try heuristic extraction from brand name if URL missing
    if not brand_domain:
        brand = _extract_possible_brand(claim)
        if brand:
            brand_domain = f"{brand}.com"

    # --- Step 2: Try verifying using official domain first ---
    if brand_domain:
        domain_query = f"site:{brand_domain} {claim}"
        print(f" Trying official site search: {domain_query}")
        official_result = _search_and_verify(domain_query, [brand_domain])
        if official_result:
            return official_result

    # --- Step 3: Fallback — general web search ---
    print(" Falling back to global web search.")
    if direct_result := _search_and_verify(claim):
        return direct_result

    try:
        smart_query = _generate_search_query(claim, llm)
        if smart_query:
            smart_result = _search_and_verify(smart_query)
            if smart_result:
                return smart_result
    except Exception as e:
        print(f"Smart query generation failed: {e}")

    return None


# --- Async parallel version ---
_executor = ThreadPoolExecutor(max_workers=5)

async def async_verify_claim(claim: str, product_url: Optional[str] = None) -> Optional[str]:
    """Async wrapper to parallelize verification."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, verify_claim, claim, product_url)
