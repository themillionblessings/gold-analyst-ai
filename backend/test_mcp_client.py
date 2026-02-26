import asyncio
import json
from mcp_server import get_live_gold_spot, calculate_egyptian_gold_premium

async def main():
    print("--- AI Client Test Script: Gold Analyst ---")
    
    # Step 1: Get live gold spot price
    print("\n[AI Context]: Fetching live gold spot price via MCP Tool...")
    spot_result = await get_live_gold_spot()
    print("Spot Result:", json.dumps(spot_result, indent=2))
    
    if spot_result.get("status") != "success":
        print("Failed to get spot price. Exiting.")
        return
        
    spot_usd_per_gram = spot_result.get("price_per_gram_24k")
    
    # Scenario variables
    total_gram_weight = 20
    total_offered_price_egp = 90000
    egp_black_market_rate = 50.5
    
    # The MCP tool calculate_egyptian_gold_premium works on a per-gram basis
    # Calculate offered price per gram
    offered_price_per_gram_egp = total_offered_price_egp / total_gram_weight
    
    # Step 2: Calculate premium
    print(f"\n[AI Scenario]: User is offered {total_gram_weight}g for {total_offered_price_egp} EGP.")
    print(f"[AI Math]: That is {offered_price_per_gram_egp} EGP per gram. Black market rate is {egp_black_market_rate}.")
    print("\n[AI Context]: Analyzing premium via MCP Tool...")
    
    premium_result = await calculate_egyptian_gold_premium(
        spot_usd_per_gram=spot_usd_per_gram,
        egp_black_market_rate=egp_black_market_rate,
        offered_egp_price=offered_price_per_gram_egp
    )
    
    print("\nPremium Analysis Result:")
    print(json.dumps(premium_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
