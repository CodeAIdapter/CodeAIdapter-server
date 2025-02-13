import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from dataclasses import dataclass
from typing import List, Optional

from utils import CodeRequest

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def index():
    return "Hello, World!"
 
@app.route("/api", methods=["POST"])
def api_analyze():
    try:
        data = request.get_json(force=True)
        print("Received data:", data)  # 打印接收到的數據
        code_request = CodeRequest(
            prompt=data.get("prompt"),
            file=data.get("file"),
        )
        response = {
            "status": "success",
            "message": "Analysis completed",
            "data": {
                "prompt": code_request.prompt,
                "analyzed_files": 1 if code_request.file else 0,
                # "file_name": code_request.file.get("name") if code_request.file else None
                "file_content": code_request.file
            }
        }

        print("Prompt:", code_request.prompt)
        print("File:", code_request.file)

        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)