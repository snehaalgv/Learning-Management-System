import requests

response = requests.post("http://localhost:8000/auth/signup", json={"name": "John Doe"})
print("Status:", response.status_code)
print("Response:", response.text)