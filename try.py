import requests
import json

url = "https://api.italki.com/api/v2/teachers"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Your payload data
payload = {
    #"has_trial": 0, "has_package": 0s, 
    "teacher_info":{"origin_country_id":["ZM", "ZW"]},"has_package": 0, "teach_language":{"language":"english"},"page_size":20,"user_timezone":"America/Toronto","page":1
}

# POST request with JSON payload
response = requests.post(url, headers=headers, json=payload)

# Or if you need to format the JSON yourself:
# response = requests.post(url, headers=headers, data=json.dumps(payload))

print(f"Status code: {response.status_code}")
print(json.dumps(response.json(), indent=2))