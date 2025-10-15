# src/agents/analyst_agent.py

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from src.models.claims import FactualClaims
from src.utils.scraper import scrape_text_from_url

def extract_claims(product_url: str) -> Optional[FactualClaims]:
    """
    Orchestrates the Analyst Agent workflow to extract factual claims.
    """
    scraped_text = scrape_text_from_url(product_url)
    if not scraped_text:
        return None

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = JsonOutputParser(pydantic_object=FactualClaims)

    prompt = ChatPromptTemplate.from_template(
        template="""
        You are an expert Analyst Agent. Your task is to extract all specific, factual, and verifiable claims from the provided product text.
        Focus only on objective claims that can be proven true or false.
        Ignore marketing fluff, subjective statements, or general benefits.
        Return the claims in the requested JSON format.

        Product Text to Analyze:
        {product_text}

        JSON Output Format Instructions:
        {format_instructions}
        """,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    try:
        result = chain.invoke({"product_text": scraped_text})
        return result
    except Exception as e:
        print(f"Error: LLM chain invocation failed. Details: {e}")
        return None