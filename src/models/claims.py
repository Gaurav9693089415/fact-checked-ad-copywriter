# src/models/claims.py

from pydantic import BaseModel, Field
from typing import List

class FactualClaims(BaseModel):
    """
    Data model for the structured output of the Analyst Agent.
    """
    claims: List[str] = Field(
        ...,
        description="A list of specific, factual claims made in the product description."
    )