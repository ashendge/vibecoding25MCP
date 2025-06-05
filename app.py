from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from prompts import get_repo_analysis_prompt
from openai_client import analyze_repository
from typing import Dict, Any, Optional
from functools import wraps
import json

app = Flask(__name__)

def create_database():
    conn = sqlite3.connect('vibe.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vibe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        github_url TEXT,
        summary TEXT,
        description TEXT,
        click_count INTEGER DEFAULT 0,
        stars_count INTEGER DEFAULT 0,
        json TEXT
    )''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect('vibe.db')
    conn.row_factory = sqlite3.Row
    return conn

def handle_db_errors(f):
    """Decorator to handle database errors."""
    @wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except sqlite3.Error as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    return wrapper

@app.route('/')
def index():
    conn = sqlite3.connect('vibe.db')
    c = conn.cursor()
    c.execute('SELECT * FROM vibe')
    tasks = c.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)
    #return jsonify(tasks)

@app.route('/submit', methods=['POST'])
def add_vibe():
    name = request.form.get('name')
    github_url = request.form.get('github_url')
    if not name or not github_url:
        return jsonify({"error": "Missing required fields"}), 400

    conn = sqlite3.connect('vibe.db')
    c = conn.cursor()
    try:
        c.execute('SELECT id FROM vibe WHERE name = ?', (name,))
        existing = c.fetchone()
        if existing:
            c.execute('UPDATE vibe SET github_url = ? WHERE name = ?', (github_url, name))
        else:
            c.execute('INSERT INTO vibe (name, github_url) VALUES (?, ?)', (name, github_url))
        conn.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

    update_vibe_description(name, github_url)
    return redirect(url_for('index'))


@app.route('/description', methods=['POST'])
@handle_db_errors
async def update_vibe_description(name: str, github_url: str):
    """
    Update the description of a vibe based on repository analysis.
    
    Args:
        name (str): The name of the repository
        
    Returns:
        JSON response with the analysis results or error message
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
        
    github_url = data.get('github_url')
    if not github_url:
        return jsonify({"error": "Missing 'github_url' in request"}), 400

    # Generate and process the prompt
    prompt = get_repo_analysis_prompt(name, github_url)
    try:
        analysis = await analyze_repository(prompt)
    except Exception as e:
        return jsonify({"error": f"Failed to analyze repository: {str(e)}"}), 500

    # Extract summary and description from the analysis
    summary = analysis.get('summary')
    description = analysis.get('description')
    if not summary or not description:
        return jsonify({"error": "Analysis did not provide required fields"}), 400

    # Update the database
    conn = sqlite3.connect('vibe.db', uri=True)
    c = conn.cursor()
    try:
        conn.execute(
            'UPDATE vibe SET summary = ?, description = ? WHERE name = ?',
            (summary, description, name)
        )
        conn.commit()
        return jsonify({
            "message": "Description updated successfully",
            "summary": summary,
            "description": description
        })
    finally:
        conn.close()



@app.route('/delete/<int:vibe_id>')
def delete_vibe(vibe_id):
    conn = sqlite3.connect('vibe.db')
    c = conn.cursor()
    c.execute('DELETE FROM vibe WHERE id = ?', (vibe_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route("/search", methods=["POST"])
def search_repo():
    data = request.json
    name = data.get("name")
    github_url = data.get("github_url")
    summary = data.get("summary")
    description = data.get("description")
    click_count = data.get("click_count")
    star_count = data.get("star_count")
    json_data = data.get("json")

    if not github_url or not name:
        return jsonify({"error": "Missing 'name' or 'github_url'"}), 400

    json_data = json.dumps(my_dict)
    return json_data

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)

