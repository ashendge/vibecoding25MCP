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

    prompt = (
        f"{name} provided this GitHub repository: {github_url}\n"
        f"Please visit this repository and determine whether it contains code, documentation, "
        f"or references related to MCP (Model Context Protocol).\n\n"
        f"Give a reasoned answer based on what you see in the repository."
    )

    answer = ask_copilot(prompt)
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

