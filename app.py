import os
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
from dataclasses import dataclass
from typing import List, Optional
from utils.llm.openai import OpenAIChat
from service import TSID
from service.deploy import k8s

from utils import CodeRequest

intro = """CodeAIdapter 是一款旨在協助開發者更有效率地解決程式問題的工具。我們提供以下服務：
1. 版本轉換
2. 語言轉換：不同程式語言之間的轉換
3. 效能優化
4. 程式debug：編譯錯誤
5. 程式debug：執行錯誤

無論您是新手還是資深開發者，CodeAIdapter 都能幫助您更輕鬆地應對各種程式挑戰！"""

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
            filename=data.get("filename"),
        )
        print(code_request, file=sys.stderr)

        cs = {
            1: "版本轉換",
            2: "語言轉換：不同程式語言之間的轉換",
            3: "效能優化",
            4: "程式debug：找出程式的錯誤，並回傳可以成功執行的程式",
            5: "部署請求",
        }
        cs_str = "\n".join([f"{key}: {value}" for key, value in cs.items()])
        dev_prot = (
            "請幫我將使用者的需求分類為以下幾項，只能回傳需求的編號，不能包含任何其他字串\n"
            "若非程式相關技術問題請回傳-1\n"
            "若為技術問題，請根據使用者附的程式分析來源程式是什麼語言，再根據使用者的prompt分析目標程式分別是什麼語言，若其中任一為python, java外的語言，請回傳0\n"
            "若為以下未條列的技術問題也請回傳0：\n"
            f'{cs_str}\n'
        )
        
        usr_prot = f'{code_request.prompt}\n'
        if code_request.filename: usr_prot += f'source file name: {code_request.filename}\n'
        if code_request.file: usr_prot += f'source code: \n{code_request.file}\n'

        print('prompt:', dev_prot, usr_prot, file=sys.stderr)

        gpt = OpenAIChat()
        response = gpt.chat(dev_prot, usr_prot)
        print('response: ', response, file=sys.stderr)

        if not isinstance(response, str):
            raise ValueError(f'Invalid response by llm: {response}')
        class_code = int(response)
        if class_code <= 0:
            if class_code == -1:
                ret_msg = "非程式相關技術問題\n\n"
            else:
                ret_msg = "抱歉，目前不支援您的需求\n\n"
            ret_msg += intro
            return ret_msg, 200
        
        if class_code not in cs:
            raise ValueError(f'Invalid class code: {class_code}')
        
        assert 1 <= class_code <= 5
        if class_code < 5:
            task = "B"
            if class_code == 1:
                task = "A1"
            elif class_code == 2:  
                task = "A2"
            elif class_code == 3:
                task = "A3"
            code_res = TSID.StartProcess(code_request.file , task, code_request.prompt)
        else:
            code_res = k8s.deploy_handle(code_request.prompt, code_request.filename, code_request.file)
        
        if code_res.status == False:
            response = {
                "file": "",
                "filename": "",
                "message": code_res.error_msg
            }
        else:
            response = {
                "file": code_res.file,
                "filename": code_res.filename,
                "message": code_res.success_msg
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
