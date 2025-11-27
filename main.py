from graph import app

def main():
    print("Starting Gold Analysis Workflow...")
    print("-----------------------------------")
    
    # Initialize with empty state
    initial_state = {}
    
    # Run the graph
    result = app.invoke(initial_state)
    
    print("\n--- FINAL ANALYSIS ---")
    print(result.get("analysis", "No analysis generated."))
    
    print("\n--- RAW DATA ---")
    print(f"Gold Data: {result.get('gold_data')}")
    # print(f"News: {result.get('market_news')}") # Uncomment to see full news

if __name__ == "__main__":
    main()
