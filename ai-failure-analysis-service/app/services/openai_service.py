import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.model = os.getenv("CHAT_MODEL")

    def analyze_failure(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert QA automation failure analysis engine. "
                        "Always return structured JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

    def decide_tools(self, failure_data, analysis: dict, repeat_count: int) -> dict:
        """
        Agent brain — LLM decides which tools to call based on
        failure context. Returns a JSON decision object.
        """
        failure_type = analysis.get("failureType", "UNKNOWN").upper()
        confidence = analysis.get("confidence", "LOW").upper()
        is_transient = analysis.get("isTransient", False)

        prompt = f"""
You are an intelligent QA agent deciding what to investigate about a test failure.

Current Failure:
- Test Name: {failure_data.testName}
- Failure Type: {failure_type}
- Confidence: {confidence}
- Is Transient: {is_transient}
- Repeat Count (same failure type seen before): {repeat_count}
- Exception: {failure_data.exceptionMessage}

Available tools:
1. re_analyze — Use when confidence is LOW. Re-analyzes with sharper focus.
2. check_environment_pattern — Use when repeat_count >= 1. Checks if failures are in one environment or many.
3. check_same_page_failures — Use when failure type contains any of these words: ELEMENT, TIMEOUT, VISIBILITY, LOCATOR, STALE, CLICKABLE, PRESENT. Checks if other tests on same page are also failing.

Rules:
- You can call multiple tools if needed.
- Only call a tool if it genuinely adds value.
- Always call check_environment_pattern if repeat_count >= 1.
- Always call check_same_page_failures if failure type contains ELEMENT, TIMEOUT, VISIBILITY, LOCATOR, STALE, CLICKABLE, or PRESENT.
- Always call re_analyze if confidence is LOW.
- If none of the above conditions are met, return empty tools list.

Return ONLY valid JSON. No explanation outside JSON.

JSON FORMAT:
{{
    "tools_to_call": [],
    "reasoning": ""
}}

tools_to_call can contain any combination of:
["re_analyze", "check_environment_pattern", "check_same_page_failures"]
or empty list [] if no tools needed.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a QA agent decision engine. "
                        "Return only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

        raw = response.choices[0].message.content
        try:
            decision = json.loads(raw)
        except Exception:
            clean = raw.replace("```json", "").replace("```", "").strip()
            try:
                decision = json.loads(clean)
            except Exception:
                print(f"[AGENT] Tool decision parse failed. Raw: {raw}\n")
                decision = {"tools_to_call": [], "reasoning": "parse error"}

        print(f"\n[AGENT] Tool decision: {decision}\n")
        return decision