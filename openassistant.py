import requests

API_URL = "https://api-inference.huggingface.co/models/zhayunduo/roberta-base-stocktwits-finetuned"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "我喜欢",
})
print(output)