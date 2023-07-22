import requests
import json

url = "https://run.cerebrium.ai/llamav2-7b-webhook/predict"

payload = json.dumps({"prompt": "who are you man"})

headers = {
  'Authorization': 'public-',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)