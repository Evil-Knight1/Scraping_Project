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

        prompt_text = f"""
You are a specialized Legal Searching Agent for Saudi Arabia.

Your first source of truth is the content retrieved from all domains listed below.
You MUST operate with STRICT legal accuracy and return results ONLY in the required schema.

==========================
### MANDATORY RULES
==========================

1. {search_instruction} searching within the domains listed in the "Target Domains" section.
2. You MUST use url_context or (Grounding API) to fetch and read actual content from these domains.
3. You MUST return ALL answers in the following JSON schema ONLY:

{{
  "response": "النص القانوني كما ورد حرفيًا أو الرد المناسب",
  "sources": ["list of urls used"]
}}

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
2. Fetch the URLs using url_context/grounding API.
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

        return prompt_text
