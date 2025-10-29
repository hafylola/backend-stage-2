import requests
import json

BASE_URL = 'http://localhost:8000'

def test_endpoint(method, endpoint, data=None):
    try:
        if method == 'GET':
            response = requests.get(f'{BASE_URL}{endpoint}')
        elif method == 'POST':
            response = requests.post(f'{BASE_URL}{endpoint}', json=data)
        elif method == 'DELETE':
            response = requests.delete(f'{BASE_URL}{endpoint}')

        print(f'{method} {endpoint} → Status: {response.status_code}')
        if response.status_code != 200:
            print(f'   Response: {response.text[:100]}...')
        return response.status_code == 200
    except Exception as e:
        print(f'{method} {endpoint} → ERROR: {e}')
        return False

print("🧪 FINAL API TEST")
print("=" * 50)

# Test all endpoints
test_endpoint('GET', '/countries')
test_endpoint('GET', '/countries?region=Africa')
test_endpoint('GET', '/countries?currency=USD&sort=gdp_desc')
test_endpoint('GET', '/countries/Nigeria')
test_endpoint('GET', '/status')
test_endpoint('GET', '/countries/image')
test_endpoint('POST', '/countries/refresh')
test_endpoint('DELETE', '/countries/TestCountry/delete')  # This will 404, which is fine

print("=" * 50)
print("✅ Testing complete! Check if all endpoints return proper status codes.")



