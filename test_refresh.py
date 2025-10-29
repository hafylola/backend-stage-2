import requests

# Test the refresh endpoint
response = requests.post('http://localhost:8000/countries/refresh')
print("Status Code:", response.status_code)
print("Response:", response.json())

