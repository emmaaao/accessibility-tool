import json

from anthropic import Anthropic
import os
from dotenv import load_dotenv
from src.vision_analyzer import analyze_image_with_vision

from src.semantic_validator import (
    analyze_links,
    analyze_alt_text,
    analyze_readability,
    enrich_elements
)

load_dotenv()


class AIAnalyzer:
    """
    Combines rule-based accessibility checks with AI-driven
    semantic analysis using the Claude API.
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def analyze(self, elements: dict) -> dict:
        """
               Main entry point for AI analysis.

               Steps:
               1. Enrich elements with semantic roles
               2. Analyze links, images, and text blocks with AI
               3. Return structured semantic analysis and AI advice
               """

        print("Enriching elements with semantic roles...")
        enriched = enrich_elements(elements)

        print("Analyzing links with AI...")
        links_advice = self._analyze_links_with_ai(enriched["links"])

        print("Analyzing images with AI...")
        images_advice = self._analyze_images_with_ai(enriched["images"])

        print("Analyzing text readability with AI...")
        text_advice = self._analyze_text_blocks(enriched["text_blocks"])

        return {
            "semantic_analysis": enriched,
            "ai_advice": {
                "links": links_advice,
                "images": images_advice,
                "text_blocks": text_advice
            }
        }

    def _analyze_links_with_ai(self, links: list) -> list:
        """
        Evaluates link purpose in context using WCAG 2.4.4.
        Combines rule-based vague link detection with AI-based contextual interpretation
        """
        results = []

        for link in links[:10]:
            rule_result = analyze_links(link)

            prompt = f"""You are a WCAG accessibility expert. Analyze this link for WCAG 2.4.4 (Link Purpose in Context).

Link Text: "{link.get('text')}"
Destination: {link.get('href')}
Context: {link.get('context', 'No context available')}
Semantic Role: {link.get('semantic_role', 'unknown')}

Evaluate whether a screen reader user can understand this link's purpose without visual context.

Respond with ONLY a JSON object (no markdown backticks):
{{
  "is_accessible": true or false,
  "wcag_criterion": "2.4.4",
  "severity": "critical" or "serious" or "moderate" or "minor" or null,
  "issue": "brief description if problematic, or null",
  "recommendation": "specific improvement or null",
  "reasoning": "brief explanation"
}}"""

            try:
                ai_result = self._ask_claude(prompt)
                parsed = self._parse_json_response(ai_result)
            except Exception as e:
                print(f"AI analysis failed for link '{link.get('text')}': {e}")
                parsed = {"error": str(e)}

            results.append({
                "link": link,
                "rule_based": rule_result,
                "ai_analysis": parsed
            })

        return results

    def _analyze_images_with_ai(self, images: list) -> list:
        """
            Evaluates alt text quality using WCAG 1.1.1.
            Combines rule-based alt text validation with AI interpretation of context and vision-based semantic consistency check
        """
        results = []
        for image in images[:10]:
            rule_result = analyze_alt_text(image)

            prompt = f"""You are a WCAG accessibility expert. Analyze this image's alt text for WCAG 1.1.1 (Non-text Content).

            Alt Text: "{image.get('alt', '(missing)')}"
            Context: {image.get('context', 'No context available')}
            Is Decorative: {image.get('is_decorative', False)}
            Semantic Role: {image.get('semantic_role', 'unknown')}

            Evaluate whether the alt text appropriately describes the image for screen reader users.

            Respond with ONLY a JSON object (no markdown backticks):
            {{
              "is_accessible": true or false,
              "wcag_criterion": "1.1.1",
              "severity": "critical" or "serious" or "moderate" or "minor" or null,
              "issue": "brief description if problematic, or null",
              "recommendation": "specific alt text suggestion or null",
              "reasoning": "brief explanation"
            }}"""

            try:
                ai_result = self._ask_claude(prompt)
                parsed = self._parse_json_response(ai_result)
                vision_result = analyze_image_with_vision(
                    image=image,
                    # Cross-check AI reasoning with vision-based image meaning
                    vision_description=parsed.get("reasoning", "")
                )
                parsed["vision_validation"] = vision_result
            except Exception as e:
                print(f" AI analysis failed for image: {e}")
                parsed = {"error": str(e),
                          "is_accessible": None
                          }

            results.append({
                "image": image,
                "rule_based": rule_result,
                "ai_analysis": parsed,
            })
        return results

    def _analyze_text_blocks(self, blocks: list) -> list:
        """
           Evaluates text complexity using WCAG 3.1.5 (Reading Level).
        """
        results = []

        for block in blocks[:5]:
            readability = analyze_readability(block.get("text", ""))

            prompt = f"""You are a WCAG accessibility expert. Analyze this text for WCAG 3.1.5 (Reading Level).

Text: "{block.get('text')[:500]}"
Word Count: {block.get('word_count', 0)}
Heading: {block.get('heading_context', 'No heading')}
Semantic Role: {block.get('semantic_role', 'unknown')}

Current readability: {readability.get('level')} 
(avg {readability.get('avg_words_per_sentence')} words/sentence)

Evaluate whether this text is understandable for a broad audience (general public education level).

Respond with ONLY a JSON object (no markdown backticks):
{{
  "is_accessible": true or false,
  "wcag_criterion": "3.1.5",
  "severity": "moderate" or "minor" or null,
  "issue": "brief description if too complex, or null",
  "recommendation": "how to simplify or null",
  "reasoning": "brief explanation"
}}"""

            try:
                ai_result = self._ask_claude(prompt)
                parsed = self._parse_json_response(ai_result)
            except Exception as e:
                print(f" AI analysis failed for text block: {e}")
                parsed = {"error": str(e)}

            results.append({
                "text_block": block,
                "readability": readability,
                "ai_analysis": parsed
            })

        return results

    def _ask_claude(self, prompt: str) -> str:
        #Send prompt to Claude and return response text
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text

    def _parse_json_response(self, response: str) -> dict:
        """Parse Claude's JSON response, handling Markdown code blocks"""
        # Remove Markdown code blocks if present
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except Exception as e:
            return {
                "is_accessible": None,
                "issue": "Invalid AI response format",
                "recommendation": None,
                "reasoning": str(e)
            }
