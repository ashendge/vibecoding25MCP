import openai
import os

openai.api_key = os.getenv("TOGETHER_API_KEY")
openai.api_base = "https://api.together.xyz/v1"

def ask_copilot(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[
                {"role": "system", "content": "You're a helpful coding assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Together API error: {str(e)}"

