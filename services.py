from google.genai.types import Tool, GoogleSearch, UrlContext
import os
import base64
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()


class GoogleGeminiService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"
        self.tools = [
            types.Tool(url_context=types.UrlContext()),
            types.Tool(google_search=types.GoogleSearch()),
        ]

        # 1. Construct a domain-specific context string

    def domain_context(self, domains: Optional[List[str]] = None):
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

    def search(self, query: str, domains: List[str]):
        domain_context = self.domain_context(domains)
        prompt_text = f"""
You are a specialized Legal Searching Agent for Saudi Arabia.

Your ONLY source of truth is the content retrieved from the domains listed below.
You MUST operate with STRICT legal accuracy and return results ONLY in the required schema.

==========================
### MANDATORY RULES
==========================

1. Search ONLY within the domains listed in the "Target Domains" section.
2. You MUST use url_context to fetch and read actual content from these domains.
3. You MUST return ALL answers in the following JSON schema ONLY:

{{
  "response": "النص القانوني كما ورد حرفيًا أو الرد المناسب",
  "sources": ["list of urls used"]
}}

4. You MUST provide legal terms exactly as they appear in the source.
   - No simplification.
   - No rephrasing.
   - No interpretation beyond what is textually written.

5. NEVER rely on general knowledge.

6. If the required information does NOT exist in the fetched content:
   You MUST return EXACTLY:

{{
  "response": "لا يوجد معلومات متاحة في المصادر المحددة.",
  "sources": ["list of urls that were checked"]
}}

==========================
### TASK
==========================

1. Search the allowed domains for any page relevant to the query.
2. Fetch the URLs using url_context.
3. Extract the legal text EXACTLY as written (articles, clauses, regulations, decisions, circulars...).
4. Provide the answer ONLY if the legal information exists in the fetched text.
5. Return the results STRICTLY using the JSON schema above.

==========================
### Query
{query}

==========================
### Target Domains (to search using url_context)
{domain_context}
"""

        return prompt_text

    def get_updated_laws(self, date: str, domains: List[str]):
        domain_context = self.domain_context(domains)
        prompt_text = f"""
        أنت باحث متخصص في القوانين واللوائح والتشريعات السعودية.

❗ مهمتك:
ابحث داخل المواقع الموجودة حصرياً في قائمة "sources" المرفقة لك عبر النظام (Grounding API)، ولا تعتمد على أي معرفة خارج هذه المواقع.

❗ المطلوب:
استخرج كل التحديثات القانونية، اللوائح، التشريعات، القرارات، التعميمات، التعديلات الدستورية، والتحديثات القانونية ذات الصلة.

ابدأ البحث من تاريخ: "{date}" 
أو ما يوازي هذا التاريخ بالتقويم الهجري.

❗ طريقة عرض النتائج:
أعد النتائج في شكل JSON مطابق تماماً للمخطط التالي:

[
  {{
    "title": "...",
    "url": "..."
  }}
]

الروابط:
{domain_context}

❗ تعليمات مهمة:
- استخدم فقط الروابط التي تأتي من المصادر المربوطة بالطلب.
- تجاهل أي روابط غير قانونية أو غير موثوقة.
- لا تضف نصوصاً إضافية خارج الـ JSON.
- يجب أن يكون كل عنوان مأخوذ مباشرة من صفحة القرار أو الإعلان القانوني.
- إذا وجدت تحديثات متعددة، أدرجها كلها.
    """
        return prompt_text
