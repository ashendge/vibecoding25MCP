from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from prompts import get_repo_analysis_prompt
from openai_client import analyze_repository
from typing import Dict, Any, Optional
from functools import wraps
import json
import requests

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
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
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
def submit():
    try:
        name = request.form.get('name')
        github_url = request.form.get('github_url')
        
        if not name or not github_url:
            return jsonify({'error': 'Name and GitHub URL are required'}), 400
            
        conn = sqlite3.connect('vibe.db')
        cursor = conn.cursor()
        
        try:
            # Check if vibe exists
            cursor.execute('SELECT id FROM vibe WHERE name = ?', (name,))
            existing_vibe = cursor.fetchone()
            
            if existing_vibe:
                # Update existing vibe
                cursor.execute('''
                    UPDATE vibe 
                    SET github_url = ?
                    WHERE name = ?
                ''', (github_url, name))
            else:
                # Insert new vibe
                cursor.execute('''
                    INSERT INTO vibe (name, github_url)
                    VALUES (?, ?)
                ''', (name, github_url))
            
            conn.commit()

            # Call the /description POST route internally
            try:
                desc_response = requests.post(
                    url_for('update_vibe_description', _external=True),
                    json={"name": name, "github_url": github_url}
                )
                # Optionally, you can check desc_response.status_code or log desc_response.json()
            except Exception as e:
                print(f"Failed to call /description: {e}")

            return redirect(url_for('index'))
            
        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
            
        finally:
            conn.close()

    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/description', methods=['POST'])
@handle_db_errors
def update_vibe_description(name: str = None, github_url: str = None):
    """
    Update the description of a vibe based on repository analysis.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    name = data.get('name', name)
    github_url = data.get('github_url', github_url)
    if not name or not github_url:
        return jsonify({"error": "Missing 'name' or 'github_url' in request"}), 400

    # Generate and process the prompt
    prompt = get_repo_analysis_prompt(name, github_url)
    try:
        import asyncio
        analysis = asyncio.run(analyze_repository(prompt))
    except Exception as e:
        return jsonify({"error": f"Failed to analyze repository: {str(e)}"}), 500

    summary = analysis.get('summary')
    description = analysis.get('description')
    if not summary or not description:
        return jsonify({"error": "Analysis did not provide required fields"}), 400

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

@app.route("/search", methods=["GET"])
def search_repo():
    """
    Search and return all vibes from the database as JSON.
    
    Query Parameters:
        top (int, optional): If provided, order results by click_count DESC and limit to this number.
        
    Returns:
        JSON response containing all vibes with their details
    """
    top = request.args.get('top', type=int)
    conn = sqlite3.connect('vibe.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    c = conn.cursor()
    try:
        if top is not None:
            c.execute('SELECT id, name, github_url, summary, description, click_count, stars_count, json FROM vibe ORDER BY click_count DESC LIMIT ?', (top,))
        else:
            c.execute('SELECT id, name, github_url, summary, description, click_count, stars_count, json FROM vibe')
        rows = c.fetchall()
        
        # Convert rows to list of dictionaries
        vibes = []
        for row in rows:
            vibe = {
                'id': row['id'],
                'name': row['name'],
                'github_url': row['github_url'],
                'summary': row['summary'],
                'description': row['description'],
                'click_count': row['click_count'],
                'stars_count': row['stars_count'],
                'json': row['json']
            }
            vibes.append(vibe)
            
        return jsonify({
            'status': 'success',
            'count': len(vibes),
            'data': vibes
        })
    except sqlite3.Error as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500
    finally:
        conn.close()

@app.route("/fetch/<name>", methods=["GET"])
def fetch_vibe(name):
    """
    Fetch a specific vibe by name from the database.
    
    Args:
        name (str): The name of the vibe to fetch
        
    Returns:
        JSON response containing the vibe details or error message
    """
    conn = sqlite3.connect('vibe.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('''
            SELECT id, name, github_url, summary, description, click_count, stars_count, json 
            FROM vibe 
            WHERE name = ?
        ''', (name,))
        row = c.fetchone()
        
        if row:
            vibe = {
                'id': row['id'],
                'name': row['name'],
                'github_url': row['github_url'],
                'summary': row['summary'],
                'description': row['description'],
                'click_count': row['click_count'],
                'stars_count': row['stars_count'],
                'json': row['json']
            }
            return jsonify({
                'status': 'success',
                'data': vibe
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'No vibe found with name: {name}'
            }), 404
            
    except sqlite3.Error as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500
    finally:
        conn.close()

@app.route("/fetch_top_trending", methods=["GET"])
def fetch_top_trending():
    """
    Fetch the top trending vibes based on click_count and stars_count.
    
    Query Parameters:
        count (int): Number of vibes to return (default: 6)
        
    Returns:
        JSON response containing the top trending vibes
    """
    count = request.args.get('count', default=2, type=int)
    conn = sqlite3.connect('vibe.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute('''
            SELECT id, name, github_url, summary, description, click_count, stars_count, json 
            FROM vibe 
            ORDER BY click_count DESC, stars_count DESC 
            LIMIT ?
        ''', (count,))
        rows = c.fetchall()
        
        vibes = []
        for row in rows:
            vibe = {
                'id': row['id'],
                'name': row['name'],
                'github_url': row['github_url'],
                'summary': row['summary'],
                'description': row['description'],
                'click_count': row['click_count'],
                'stars_count': row['stars_count'],
                'json': row['json']
            }
            vibes.append(vibe)
            
        return jsonify({
            'status': 'success',
            'count': len(vibes),
            'data': vibes
        })
    except sqlite3.Error as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500
    finally:
        conn.close()

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)

