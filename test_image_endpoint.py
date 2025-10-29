import requests

# Test the image endpoint
response = requests.get('http://localhost:8000/countries/image')
print("Status Code:", response.status_code)
print("Content-Type:", response.headers.get('content-type'))
if response.status_code == 200:
    print("✅ SUCCESS: Image endpoint is working!")
    # Save the image to verify it's correct
    with open('test_output.png', 'wb') as f:
        f.write(response.content)
    print("Image saved as test_output.png")
else:
    print("❌ FAILED:", response.json())