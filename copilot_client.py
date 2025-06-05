import os
import requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

def ask_copilot(prompt):
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }

    json_data = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.3,
            "max_new_tokens": 200,
        }
    }
    model_id = "distilgpt2"
    model_url = f"https://api-inference.huggingface.co/models/{model_id}"



#model_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

    try:
        response = requests.post(model_url, headers=headers, json=json_data, timeout=30)
        response.raise_for_status()
        outputs = response.json()
        return outputs[0]['generated_text']
    except Exception as e:
        return f"HuggingFace API error: {str(e)}"

