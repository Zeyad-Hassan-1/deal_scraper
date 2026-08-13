from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    query = request.args.get('query')
    max_price = request.args.get('max_price')
    item_count = request.args.get('item_count', '10')

    if not query or not max_price:
        return jsonify({"error": "Missing query or max_price"}), 400

    cmd = [
        "python3", "run_local_spiders.py",
        "--query", query,
        "--max_price", max_price,
        "--item_count", item_count
    ]
    
    try:
        # Run the local spiders script
        print(f"Running scraper with args: {cmd}")
        subprocess.run(cmd, check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Read the generated JSON results
        results = []
        data_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
        
        jumia_path = os.path.join(data_dir, "jumia_laptops.json")
        twob_path = os.path.join(data_dir, "2b_laptops.json")
        
        if os.path.exists(jumia_path):
            with open(jumia_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    results.extend(json.loads(content))
                    
        if os.path.exists(twob_path):
            with open(twob_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    results.extend(json.loads(content))
                    
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
