from services.scholar_service import get_author_h_index
import json

def test_fetch(name):
    print(f"Fetching '{name}'...")
    result = get_author_h_index(name)
    if result:
        print(f"Result: {result['name']} (H:{result.get('h_index')} or {result.get('hIndex')})")
        print(json.dumps(result, indent=2))
    else:
        print("Not found")

test_fetch("Andrew Ng")
