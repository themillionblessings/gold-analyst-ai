import os
import json
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load config
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except:
    config = {}

class GoldAnalystEngine:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = "gemini-2.5-flash-preview-09-2025" # Using Flash for speed/cost
        self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0.0) # Deterministic
        
    def analyze(self, gld_data, xau_data):
        if not self.api_key:
            return self._mock_response("Error: Missing GOOGLE_API_KEY")
            
        # Construct Input JSON
        input_payload = {
            "timestamp_utc": gld_data.get("timestamp_utc"),
            "assets": {
                "GLD": gld_data,
                "XAU": xau_data
            },
            "derived": {
                "recent_trend_slope": 0.0, # Placeholder for advanced logic
                "short_volatility": 0.0,   # Placeholder
                "notes": "Analyze based on price action and technicals."
            },
            "config": {
                "risk_tiers": list(config.get("risk_tiers", {}).keys()),
                "mapping_thresholds": config.get("mapping_thresholds", {})
            }
        }
        
        # System Prompt
        system_prompt = """
        You are an expert Gold Analyst AI.
        Your task is to provide ultra-minimal Buy/Hold/Sell recommendations for Gold.
        
        Tone: Ultra-minimal, direct, professional.
        Output: STRICT JSON only. No markdown, no preamble.
        
        Required Output Schema:
        {
          "recommendation": "BUY|HOLD|SELL",
          "confidence": <float 0-100>,
          "rationale_brief": "One-line ultra-minimal explanation (max 20 words)",
          "rationale_technical": "One short paragraph technical rationale (max 80 words)",
          "suggested_risk_tier": "Conservative|Moderate|Aggressive"
        }
        
        Rules:
        1. If confidence < 50%, include a calibration sentence in rationale.
        2. Never promise returns.
        3. Be deterministic based on the provided data.
        """
        
        # User Prompt
        user_prompt = f"""
        Analyze this market data:
        {json.dumps(input_payload, indent=2)}
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Clean up if model adds markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            output_json = json.loads(content.strip())
            
            # Apply Deterministic Mapping
            final_recommendation = self._map_recommendation(output_json)
            output_json["final_action"] = final_recommendation
            output_json["position_size"] = self._get_position_size(output_json.get("suggested_risk_tier"))
            
            return {
                "input": input_payload,
                "output": output_json
            }
            
        except Exception as e:
            return self._mock_response(f"AI Error: {str(e)}")

    def _map_recommendation(self, output_json):
        rec = output_json.get("recommendation", "HOLD").upper()
        conf = float(output_json.get("confidence", 0))
        thresholds = config.get("mapping_thresholds", {"confidence_buy": 60, "confidence_sell": 60})
        
        if rec == "BUY" and conf >= thresholds["confidence_buy"]:
            return "BUY"
        elif rec == "SELL" and conf >= thresholds["confidence_sell"]:
            return "SELL"
        else:
            return "HOLD"

    def _get_position_size(self, tier):
        tiers = config.get("risk_tiers", {})
        return tiers.get(tier, "0.0%")

    def _mock_response(self, error_msg):
        return {
            "input": {},
            "output": {
                "recommendation": "HOLD",
                "confidence": 0,
                "rationale_brief": error_msg,
                "rationale_technical": "System error or missing API key.",
                "suggested_risk_tier": "Conservative",
                "final_action": "HOLD",
                "position_size": "0.0%"
            }
        }
