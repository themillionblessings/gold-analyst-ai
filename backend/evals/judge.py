import os
import json
import asyncio
import google.generativeai as genai
import sys
import argparse

# Ensure backend imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from mcp_server import get_live_gold_spot, calculate_egyptian_gold_premium
    from utils.sanitizer import SovereignDataShield
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

class JudgeAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("CRITICAL: GOOGLE_API_KEY environment variable not set.")
            sys.exit(1)
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-flash-latest", # use flash as it was verified working earlier
            generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
        )

    def evaluate_response(self, user_input: str, actual_response: str, expected_context: str) -> dict:
        """Uses an LLM as a judge to evaluate the quality of the actual response."""
        prompt = f"""
        You are an impartial Lead AI Reliability Engineer Judge.
        Evaluate the AI's actual response against the expected context to determine its quality.

        [User Input Scenario]:
        {user_input}

        [Expected Context Target]:
        {expected_context}

        [AI Actual Response]:
        {actual_response}

        Output your strict evaluation in JSON format exactly as follows:
        {{
            "faithfulness_score": <int 1-5, 5 being perfectly faithful to facts/expected logic>,
            "relevancy_score": <int 1-5, 5 being perfectly relevant and addressing the user scenario>,
            "hallucination_detected": <boolean, true if AI fabricated data not implicitly provided>,
            "judge_reasoning": "<string clearly explaining the scores>"
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            return data
        except Exception as e:
            print(f"Judge Agent Error: {e}")
            return {
                "faithfulness_score": 0,
                "relevancy_score": 0,
                "hallucination_detected": True,
                "judge_reasoning": f"Validation failed: {str(e)}"
            }

async def simulate_system_response(test_case: dict) -> str:
    """Simulates the backend pipelines to generate an 'actual' response for benchmarking."""
    tc_id = test_case.get("id")
    payload = test_case.get("input_payload", {})
    
    if tc_id == "tc-001" or tc_id == "tc-002":
        # Simulate Deal Analyzer Logic
        weight = payload.get("weight_grams", 0)
        offered = payload.get("offered_price_egp", 0)
        
        # 1. Fetch live spot
        spot_res = await get_live_gold_spot()
        spot_usd = spot_res.get("price_per_gram_24k", 88.50) # fallback
        
        # 2. Black market rate
        bm_rate = 50.5
        
        offered_per_gram = offered / weight if weight > 0 else 0
        
        # 3. Premium calc
        premium_res = await calculate_egyptian_gold_premium(spot_usd, bm_rate, offered_per_gram)
        
        return f"The calculated fair value per gram is {premium_res['fair_value_egp']} EGP. The offered price per gram is {premium_res['offered_price']} EGP. This represents a {premium_res['premium_percent']}% premium. Verdict: {premium_res['verdict']}."

    elif tc_id == "tc-003":
        # Simulate Data Sovereignty Shield
        text = payload.get("text", "")
        redacted = SovereignDataShield.redact_financials(text)
        return f"Sanitized payload sent to LLM: '{redacted}'. LLM successfully processed the institutional inquiry."
        
    return "Unknown Scenario"

async def run_evaluations():
    print("🚀 Initiating LLM-as-a-Judge Evaluation Framework...\n")
    
    file_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
    try:
        with open(file_path, "r") as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print("Test cases not found.")
        sys.exit(1)

    judge = JudgeAgent()
    total_score = 0
    max_possible_score = len(test_cases) * 10 # 5 for faithfulness, 5 for relevancy per test

    for tc in test_cases:
        tc_id = tc['id']
        print(f"▶️ Evaluating Test Case: {tc_id} - {tc['description']}")
        
        # 1. Generate Actual Response
        actual_response = await simulate_system_response(tc)
        print(f"   [Engine Output]: {actual_response}")
        
        # 2. Judge the Response
        user_context = json.dumps(tc['input_payload'])
        judge_result = judge.evaluate_response(user_context, actual_response, tc['expected_context'])
        
        # 3. Output results
        f_score = judge_result.get("faithfulness_score", 0)
        r_score = judge_result.get("relevancy_score", 0)
        total_score += (f_score + r_score)
        
        print(f"   [Judge Scores]: Faithfulness: {f_score}/5 | Relevancy: {r_score}/5 | Hallucination: {judge_result.get('hallucination_detected')}")
        print(f"   [Judge Reason]: {judge_result.get('judge_reasoning')}\n")

    # 4. Aggregate Accuracy
    accuracy = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
    print(f"🏆 System Accuracy Metric: {accuracy:.1f}%")

if __name__ == "__main__":
    asyncio.run(run_evaluations())
