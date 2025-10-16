

# Fact-Checked Ad Copywriter

**Fact-Checked Ad Copywriter** is an AI-powered system that automatically extracts factual claims from a product webpage, verifies them using trusted and official sources, and generates accurate and credible advertising copy.
The project ensures that marketing content is both persuasive and factually correct.

**Live Application:** [https://fact-checked-ad-copywriter-7ki5vf3kynzpscid25tb8v.streamlit.app/](https://fact-checked-ad-copywriter-7ki5vf3kynzpscid25tb8v.streamlit.app/)

---

## Overview

This project was developed as part of the **ProspelloAI Hackathon**. It demonstrates how multi-agent reasoning, retrieval-augmented generation (RAG), and web-based fact verification can be combined to produce ethical, data-driven marketing content.

The system consists of three coordinated agents:

1. **Analyst Agent** – Extracts verifiable factual claims from product descriptions.
2. **Fact-Checker Agent** – Verifies each claim using the product’s official website first, and then falls back to trusted sources across the web.
3. **Copywriter Agent** – Generates concise and compelling ad copy using only verified claims.

---

## Features

* Automatic claim extraction from any product page.
* Official-domain prioritization for fact verification.
* Asynchronous claim verification for improved performance.
* Adjustable options for claim extraction and verification limits.
* Multiple advertising tone options (Professional, Friendly, Witty, Urgent, Luxurious).
* Streamlit-based web interface with a simple and intuitive design.

---

## Architecture

```
Product URL → Analyst Agent → Fact-Checker Agent → Copywriter Agent → Verified Ad Copy
```

Built with:

* LangChain
* OpenAI GPT-4o
* Tavily API (for RAG search)
* Streamlit
* BeautifulSoup and Requests (for web scraping)

---

## Technology Stack

* **Programming Language:** Python 3.11
* **Frameworks:** LangChain, Streamlit, FastAPI (optional)
* **APIs:** OpenAI API, Tavily Search API
* **Utilities:** BeautifulSoup, Requests, Pydantic, dotenv

---

## Installation and Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Gaurav9693089415/fact-checked-ad-copywriter.git
   cd fact-checked-ad-copywriter
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv myenv
   myenv\Scripts\activate       # Windows
   # or
   source myenv/bin/activate    # Mac/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   Create a `.env` file in the project root with:

   ```
   OPENAI_API_KEY=your_openai_key_here
   TAVILY_API_KEY=your_tavily_key_here
   ```

5. **Run the application locally**

   ```bash
   streamlit run app.py
   ```

---

## Folder Structure

```
fact-checked-ad-copywriter/
│
├── app.py                     # Streamlit frontend
├── requirements.txt
├── runtime.txt
│
└── src/
    ├── agents/
    │   ├── analyst_agent.py
    │   ├── fact_checker_agent.py
    │   └── copywriter_agent.py
    ├── models/
    │   └── claims.py
    └── utils/
        └── scraper.py
```

---

## Example Output

**Input URL:**
`https://www.amazon.in/Aashirvaad-Kashmiri-Mirch-100-g/dp/B08TVGLDFT`

**Verified Claims:**

* Made from authentic Kashmiri red chilies
* 100% natural, no added preservatives

**Generated Ad Copy (Tone: Friendly):**

> Spice up your dishes with Aashirvaad Kashmiri Mirch. Made from authentic red chilies and packed with pure flavor, it brings true Kashmiri heat to every meal.

---

## Evaluation Fit (Hackathon Criteria)

| Criteria                         | Description                                                                        |
| -------------------------------- | ---------------------------------------------------------------------------------- |
| **Creativity & Innovation**      | Multi-agent AI system combining claim extraction, verification, and ad generation. |
| **Technical Depth**              | Uses RAG, LangChain, asynchronous pipelines, and LLM reasoning.                    |
| **Functionality & Completeness** | Fully working prototype with UI and live deployment.                               |
| **Presentation & Clarity**       | Clear workflow and easy-to-use interface.                                          |
| **Impact**                       | Promotes truth-based and ethical advertising.                                      |

---

## Future Improvements

* Enhanced domain detection for complex brand websites.
* Support for multiple product categories and industries.
* Integration with marketing automation platforms.
* Multi-language ad generation.
* Historical claim verification and analytics dashboard.

---

## Author

**Gaurav**
GitHub: [@Gaurav9693089415](https://github.com/Gaurav9693089415)

---

## License

This project is licensed under the **MIT License**.
You are free to use, modify, and distribute it with appropriate credit.

---


