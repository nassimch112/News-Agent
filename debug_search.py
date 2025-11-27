from duckduckgo_search import DDGS

def test_search():
    print("Testing DDGS...")
    try:
        results = DDGS().text("test", max_results=5)
        print(f"Results type: {type(results)}")
        print(f"Results: {results}")
        
        if not results:
            print("No results returned.")
        else:
            print("Success!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
