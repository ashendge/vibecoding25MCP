from flask import Flask, request, jsonify
from copilot_client import ask_copilot

app = Flask(__name__)

@app.route("/search", methods=["POST"])
def search_repo():
    data = request.json
    name = data.get("name")
    github_url = data.get("github_url")

    if not github_url or not name:
        return jsonify({"error": "Missing 'name' or 'github_url'"}), 400

    prompt = build_summary_prompt(name, github_url)

    answer = ask_copilot(prompt)
    return jsonify({"response": answer})

def build_summary_prompt(name: str, github_url: str) -> str:
    return f"""You are an AI assistant with expertise in analyzing public codebases and understanding their purpose and capabilities.

Your task is to generate a detailed summary of the project hosted at the following GitHub URL:
{github_url}

Please include:

1. A brief one-sentence summary of the entire project.
2. A comprehensive summary covering:
   - Service name
   - Purpose
   - Offered methods and API endpoints
   - Examples of how to use the endpoints and methods

Focus only on the content publicly visible at the above GitHub URL, and tailor your response to developers evaluating the project for potential use.

Respond in a clear and professional tone.
"""

    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

