
import requests
import json

def test_fetch_conferences():
    url = "https://developers.events/all-events.json"
    print(f"Fetching {url}...")
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            
            future_events = 0
            for event in data:
                if event.get('date') and len(event['date']) > 0:
                    # check if start date is > Jan 1 2024 (approx 1704067200000 ms)
                    if event['date'][0] > 1704067200000:
                        future_events += 1
            
            print(f"Total events: {len(data)}")
            print(f"Events after Jan 1 2024: {future_events}")
        else:
            print(f"Failed to fetch. Status: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch_conferences()
