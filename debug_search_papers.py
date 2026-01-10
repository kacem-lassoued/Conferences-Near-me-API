import requests

def search_papers_by_conference(conf_name, year=2023):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    query = f"{conf_name}"
    
    # We can try to use the 'venue' parameter if filtering, strictly, but 'query' is often broader.
    # Let's try a broad query first.
    params = {
        'query': query,
        'year': str(year),
        'limit': 5,
        'fields': 'title,authors,venue,year,citationCount'
    }
    
    print(f"Searching for papers for: {conf_name} in {year}...")
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            papers = data.get('data', [])
            print(f"Found {len(papers)} papers.")
            for p in papers:
                print(f"- {p['title']} ({p.get('venue')}, {p.get('year')}) - Authors: {len(p.get('authors', []))}")
        else:
            print(f"Error: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    search_papers_by_conference("NeurIPS")
    print("-" * 20)
    search_papers_by_conference("React Conf") # Likely less academic papers, but let's see
