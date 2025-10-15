# src/agents/copywriter_agent.py

from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_ad_copy(verified_claims: List[str], tone: str) -> Optional[str]:
    """
    Generates ad copy from a list of verified claims in a specific tone.
    """
    if not verified_claims:
        return "No verified claims were provided to generate ad copy."

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    parser = StrOutputParser()

    prompt = ChatPromptTemplate.from_template(
        template="""
        You are an expert marketing copywriter. Your task is to write a compelling, trustworthy, and brief advertisement using ONLY the following verified facts.

        **Instructions:**
        1.  Weave the verified facts into a persuasive and coherent ad.
        2.  The tone of the ad must be **{tone}**.
        3.  Do NOT invent any new features or benefits.
        4.  Your final output must be only the ad copy and nothing else.

        **Verified Facts:**
        {claims_list}
        """
    )

    chain = prompt | llm | parser

    try:
        claims_input = "\n".join(f"- {claim}" for claim in verified_claims)
        ad_copy = chain.invoke({"claims_list": claims_input, "tone": tone})
        return ad_copy
    except Exception as e:
        print(f"Error during ad copy generation: {e}")
        return None