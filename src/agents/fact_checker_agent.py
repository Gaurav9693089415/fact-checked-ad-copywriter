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
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

def _extract_possible_brand(claim: str) -> Optional[str]:
    """
    Simple heuristic: extract potential brand or product name from claim text.
    Example: "Apple iPhone 15 has the best camera" → 'apple'
    """
    words = claim.split()
    for w in words:
        if re.match(r"^[A-Z][a-z]+$", w):  # likely brand (capitalized single word)
            return w.lower()
    return None

def _pick_best_result(results: List[dict], trusted_domains: Optional[List[str]]) -> Optional[str]:
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
    for r in results:
        url = r.get("url")
        if url:
            return url
    return None

def _generate_search_query(claim: str, llm: ChatOpenAI) -> str:
    parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_template(
        "You are a search expert. Produce a short, focused search query to find authoritative specifications for this claim.\n\nClaim: {claim}\n\nRespond with only the search query."
    )
    chain = prompt | llm | parser
    return chain.invoke({"claim": claim}).strip()

def _verify_with_llm(claim: str, source_text: str, llm: ChatOpenAI, force_yesno: bool = False) -> Optional[bool]:
    parser = StrOutputParser()
    if force_yesno:
        template = "You are a concise fact-checker. Given the Claim and the Source Text, answer ONLY 'Yes' or 'No'.\n\nClaim: {claim}\n\nSource Text: {source_text}\n"
    else:
        template = "You are a meticulous fact-checker. Analyze whether the Source Text confirms the Claim. Answer 'Yes' or 'No'.\n\nClaim: {claim}\n\nSource Text: {source_text}\n"
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | parser
    try:
        resp = chain.invoke({"claim": claim, "source_text": source_text[:15000]})
    except Exception as e:
        print(f"LLM verification call failed: {e}")
        return None
    
    r = resp.strip().lower()
    if r.startswith("yes"): return True
    if r.startswith("no"): return False
    return None


# --- Main verification pipeline ---

def verify_claim(claim: str, trusted_domains: List[str] = None) -> Optional[str]:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    search_tool = TavilySearchResults(max_results=3)

    def _search_and_verify(query: str, preferred_domains: List[str] = None) -> Optional[str]:
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

    # Step 1: Try verifying from possible official site first
    brand = _extract_possible_brand(claim)
    if brand:
        possible_domains = [f"{brand}.com", f"{brand}.in", f"{brand}.co", f"{brand}.org"]
        for d in possible_domains:
            official_url = f"https://{d}"
            scraped_text = scrape_text_from_url(official_url)
            if scraped_text:
                verdict = _verify_with_llm(claim, scraped_text, llm)
                if verdict:
                    return official_url

    # Step 2: Tavily/Web verification fallback
    if direct_result := _search_and_verify(claim, trusted_domains):
        return direct_result
    
    try:
        if smart_query := _generate_search_query(claim, llm):
            if smart_result := _search_and_verify(smart_query, trusted_domains):
                return smart_result
    except Exception as e:
        print(f"Smart query generation failed: {e}")

    return None


# --- Async parallel version ---
_executor = ThreadPoolExecutor(max_workers=5)

async def async_verify_claim(claim: str, trusted_domains: list = None) -> Optional[str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, verify_claim, claim, trusted_domains)
