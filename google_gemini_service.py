import os
from typing import List, Optional
from google import genai
from google.genai import types
import os
import base64
from dotenv import load_dotenv


load_dotenv()


class GoogleGeminiService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"
        self.tools = [
            types.Tool(url_context=types.UrlContext()),
            types.Tool(google_search=types.GoogleSearch()),
        ]

        # 1. Construct a domain-specific context string

    def domain_context(self, domains: List[str]):
        domain_list = ", ".join(domains)
        return domain_list

    def generate_content(self, query: str):
        print(f"final searched query: {query}")
        generate_content_config = types.GenerateContentConfig(
            tools=self.tools,
            temperature=0.3,  # Lower temperature for more factual legal responses
            response_modalities=["TEXT"],
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=query),
                    ],
                ),
                config=generate_content_config,
            )

            # Return the text content
            if response.text:
                return response.text
            else:
                return "No text response generated."

        except Exception as e:
            print(f"Error generating content: {e}")
            return f"Error: {str(e)}"

    def search(self, query: str, domains: List[str], mode: Optional[bool] = False):
        domain_context = self.domain_context(domains)
        search_instruction = "Only" if mode == "strict" else "Prioritize"
        schema_instruction = {
            "Title": "string (The official title of the legal text/article)",
            "Summary": "string (A brief summary of the legal text/article)",
            "Source_name": "string (e.g., الجريدة الرسمية أو الموقع الرسمي)",
            "Date": "string (Date of issuance)",
            "Hijeri_Date": "string (Hijri date of issuance)",
            "Source_url": "string (The full URL link from the search result)(Grounding API)",
        }

        prompt_text = f"""You are a specialized Legal Searching Agent for Saudi Arabia.

Your task is to analyze content from the **Target Domains** listed below based on the **Query**, and return the relevant legal information.

==========================
### MANDATORY RULES
==========================

1. **Source of Truth:** {search_instruction} retrieving content from the domains listed in the "Target Domains" section.
2. **Schema:** You MUST return ALL results in a JSON array that STRICTLY adheres to the following schema. Use 'null' for fields where data is unavailable.

[
    {schema_instruction}
    ...
]

3. **Content Extraction:** You MUST provide legal terms **EXACTLY** as they appear in the source text. No rephrasing or simplification.

4. **Response Field (Error Handling):** If you successfully find legal text, **DO NOT** include a "response" field. If you fail to find legal text or encounter a technical issue (like the redirect error), you MUST return the following **SINGLE** JSON object with all fields set to null, and the "response" field populated:

{{
    "Title": null,
    "Summary": null,
    "Source_name": null,
    "Date": null,
    "Hijeri_Date": null,
    "Source_url": null,
    "response": "string describing the refusal or error reason."
}}

==========================
### Query
{query}

==========================
### Target Domains (for content retrieval):
{domain_context}
"""

        return prompt_text


"""
You are a specialized Legal Searching Agent for Saudi Arabia.

Your task is to analyze content from the **Target Domains** listed below based on the **Query**, and return the relevant legal information.

==========================
### MANDATORY RULES
==========================

1. **Source of Truth:** {search_instruction} retrieving content from the domains listed in the "Target Domains" section.
2. **Schema:** You MUST return ALL results in a JSON array that STRICTLY adheres to the following schema. Use 'null' for fields where data is unavailable.

[
    {{
        "Title": "string (The official title of the legal text/article)",
        "Source_Name": "string (e.g., الجريدة الرسمية أو الموقع الرسمي)",
        "Date": "string (Date of issuance)",
        "Hijeri_Date": "string (Hijri date of issuance)",
        "Source_url": "string (The full URL link from the search result)"
    }},
    ...
]
**IMPORTANT CLARIFICATION for Source_url:** When filling the "Source_url" field, you MUST use the URL provided directly by the Search Tool. DO NOT attempt to validate, follow, or resolve this URL (even if it appears to be a Google redirect link). The model's grounding snippet is sufficient for extraction.

3. **Content Extraction:** You MUST provide legal terms **EXACTLY** as they appear in the source text. No rephrasing or simplification.

4. **Response Field (Error Handling):** If you successfully find legal text, **DO NOT** include a "response" field. If you fail to find legal text or encounter a technical issue (like the redirect error), you MUST return the following **SINGLE** JSON object with all fields set to null, and the "response" field populated:

{{
    "Title": null,
    "Source_Name": null,
    "Date": null,
    "Hijeri_Date": null,
    "Source_url": null,
    "response": "string describing the refusal or error reason."
}}

==========================
### Query
{query}

==========================
### Target Domains (for content retrieval):
{domain_context}"""


"""'
You are a specialized Legal Searching Agent for Saudi Arabia.

Your first source of truth is the content retrieved from all domains listed below.
You MUST operate with STRICT legal accuracy and return results ONLY in the required schema.

==========================
### MANDATORY RULES
==========================

1. {search_instruction} searching within the domains listed in the "Target Domains" section.
2. You MUST use url_context or (Grounding API) to fetch and read actual content from these domains.
3. You MUST return ALL answers in the following JSON schema ONLY:

{schema_instruction}

4. You MUST provide legal terms exactly as they appear in the source.
   - No simplification.
   - No rephrasing.
   - No interpretation beyond what is textually written.

5. ERROR HANDLING & REFUSALS:
    - If you encounter technical issues (e.g., "vertexaisearch" redirects, tool failures, or access denied), you MUST STILL return a JSON object.
    - Place the error description or refusal reason inside the "response" field.
    - DO NOT output plain text explanations, apologies, or conversational filler outside the JSON.


==========================
### TASK
==========================

1. Search the allowed domains for any page relevant to the query.
2. You MUST use url_context or (Grounding API) to fetch and read actual content from these domains.
3. Extract the legal text EXACTLY as written (articles, clauses, regulations, decisions, circulars...).
4. Provide the answer ONLY if the legal information exists in the fetched text.
5. Return the results STRICTLY using the JSON schema above.

==========================
### Query
{query}

==========================
### Target Domains (to search using url_context):
{domain_context}
"""
