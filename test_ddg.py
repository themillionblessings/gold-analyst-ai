try:
    from duckduckgo_search import DDGS
    print("Successfully imported DDGS")
    results = DDGS().text("python", max_results=1)
    print(results)
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
