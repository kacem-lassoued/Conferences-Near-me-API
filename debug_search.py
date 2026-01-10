import requests
import json

def debug_search(name):
    url = "https://api.semanticscholar.org/graph/v1/author/search"
    params = {
        'query': name,
        'fields': 'name,hIndex,citationCount,authorId,affiliations',
        'limit': 20
    }
    resp = requests.get(url, params=params)
    data = resp.json().get('data', [])
    
    with open('debug_output.txt', 'a') as f:
        f.write(f"\n--- Search results for '{name}' ---\n")
        # Sort by h-index for display
        data.sort(key=lambda x: x.get('hIndex') or 0, reverse=True)
        for author in data:
            f.write(f"Name: {author['name']}, H-Index: {author['hIndex']}, Citations: {author['citationCount']}, ID: {author['authorId']}, Aff: {author.get('affiliations')}\n")

with open('debug_output.txt', 'w') as f:
    f.write("") # Clear file

debug_search("Andrew Ng")
debug_search("Andrew Y. Ng")
debug_search("Geoffrey Hinton")
