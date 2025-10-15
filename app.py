import streamlit as st
import os, certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
import asyncio
from dotenv import load_dotenv

from src.agents.analyst_agent import extract_claims
from src.agents.fact_checker_agent import async_verify_claim
from src.agents.copywriter_agent import generate_ad_copy

# --- Streamlit configuration ---
st.set_page_config(page_title="Fact-Checked Ad Copywriter", page_icon="✍️", layout="wide")
st.title(" Fact-Checked Ad Copywriter")
st.markdown("An AI agent pipeline that extracts factual claims, verifies them, and writes trustworthy ad copy.")

# --- Load API keys ---
load_dotenv()
if not all([os.getenv("OPENAI_API_KEY"), os.getenv("TAVILY_API_KEY")]):
    st.error("API keys for OpenAI and Tavily are not set. Please check your .env file.")
else:
    col1, col2 = st.columns(2)

    with col1:
        url_input = st.text_input("Enter a product page URL:", placeholder="https://example.com/product-page")

        # --- Extraction options ---
        extract_all = st.checkbox("Extract all claims", value=False)
        claims_extract_count = 0
        if not extract_all:
            claims_extract_count = st.number_input(
                "Number of claims to extract:",
                min_value=1, max_value=20, value=5, step=1
            )

        # --- Verification options ---
        verify_all = st.checkbox("Verify all extracted claims", value=False)
        claims_verify_count = 0
        if not verify_all:
            claims_verify_count = st.number_input(
                "Number of claims to verify:",
                min_value=1, max_value=10, value=5, step=1
            )

    with col2:
        tone_options = ["Professional", "Witty", "Urgent", "Friendly", "Luxurious"]
        selected_tone = st.selectbox("Select advertising tone:", options=tone_options)

    if st.button("Generate Ad Copy"):
        if not url_input:
            st.warning("Please enter a URL.")
        else:
            with st.spinner("Running agent pipeline..."):
                # Step 1 – Extract claims
                st.info("Step 1 of 3 – Extracting claims ")
                claims_data = extract_claims(url_input)

                if not claims_data or not claims_data.get("claims"):
                    st.error("No claims extracted.")
                else:
                    all_claims = claims_data["claims"]
                    if not extract_all:
                        all_claims = all_claims[:claims_extract_count]

                    # Step 2 – Verify claims (asynchronous)
                    st.info("Step 2 of 3 – Verifying claims ")
                    if not verify_all:
                        claims_to_verify = all_claims[:claims_verify_count]
                    else:
                        claims_to_verify = all_claims

                    async def verify_all_claims_parallel(claims):
                        tasks = [async_verify_claim(claim) for claim in claims]
                        return await asyncio.gather(*tasks)

                    with st.spinner(f"Verifying {len(claims_to_verify)} claims..."):
                        sources = asyncio.run(verify_all_claims_parallel(claims_to_verify))

                    verified_claims, verification_results = [], []
                    for claim, src in zip(claims_to_verify, sources):
                        verification_results.append((claim, src))
                        if src:
                            verified_claims.append(claim)

                    # Step 3 – Generate Ad Copy
                    st.info("Step 3 of 3 – Generating Ad ")
                    ad_copy = generate_ad_copy(verified_claims, selected_tone)

            st.success(" Pipeline Complete!")

            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader(f"Generated Ad Copy (Tone: {selected_tone})")
                st.markdown(f"> {ad_copy}" if ad_copy else "_No verified claims to generate copy._")

            with col_right:
                st.subheader("Verification Report")
                for claim, src in verification_results:
                    if src:
                        st.markdown(f" **Claim:** *{claim}*<br> Source: [{src}]({src})", unsafe_allow_html=True)
                    else:
                        st.markdown(f" **Claim:** *{claim}*<br> _Not verified_", unsafe_allow_html=True)
                    st.markdown("---")
