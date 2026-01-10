import requests
import json

def debug_search(name, limit=20):
    url = "https://api.semanticscholar.org/graph/v1/author/search"
    params = {
        'query': name,
        'fields': 'name,hIndex,citationCount,authorId',
        'limit': limit
    }
    resp = requests.get(url, params=params)
    data = resp.json().get('data', [])
    data.sort(key=lambda x: x.get('hIndex') or 0, reverse=True)
    
    with open('search_results.log', 'a') as f:
        f.write(f"\n--- Search results for '{name}' (limit={limit}, count={len(data)}) ---\n")
        if data:
            top = data[0]
            f.write(f"TOP: Name: {top['name']}, H-Index: {top['hIndex']}, ID: {top['authorId']}\n")
            
            # Check if verified Andrew Ng is in list
            found = False
            for i, a in enumerate(data):
                if a['authorId'] == '34699434':
                    found = True
                    f.write(f"FOUND TARGET! ID 34699434 found at index {i} in sorted list.\n")
                    break
            if not found:
                f.write("TARGET NOT FOUND\n")
        else:
            f.write("NO DATA\n")

with open('search_results.log', 'w') as f: f.write("")

# Test 1: Just increasing limit
debug_search("Andrew Ng", limit=100)

# Test 2: Searching with initial
debug_search("A. Ng", limit=20)

# Test 3: Topic injection
debug_search("Andrew Ng machine learning", limit=20)
