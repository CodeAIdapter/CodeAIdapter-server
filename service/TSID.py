import subprocess
import json
import tempfile
import os
import re
import sys
sys.path.append("..")
from utils.llm.openai import OpenAIChat
from utils.utils import CodeResponse

import subprocess
import json

def detect_language(code):
    if re.search(r"class\s+\w+|public\s+static\s+void\s+main", code):
        return "java"
    elif re.search(r"def\s+\w+|import\s+|print\s*\(", code):
        return "python"
    return "unknown"



def run_code(response_json):

    response_dict = json.loads(response_json)  # Parse the JSON string into a dictionary
    code = response_dict["code"]
    language = response_dict["language"]
    docker_image = response_dict["docker_image"]
    java_class_name = response_dict["class_name"]
    
    # Create a temporary directory to save the code
    with tempfile.TemporaryDirectory() as temp_dir:
        # Determine the file name based on the language
        file_name = f"{java_class_name}.java" if language == "java" else "output.py"
        file_path = os.path.join(temp_dir, file_name)
        
        # Write the code to the file
        with open(file_path, "w") as f:
            f.write(code)

        
        # Build the Docker command to run the code
        if language == "java":
            # For Java, we assume the docker image contains the necessary tools to compile and run Java code
            docker_command = [
                "docker", "run", "--rm", 
                "-v", f"{temp_dir}:/workspace", 
                docker_image, "bash", "-c", f"javac /workspace/{file_name} && java -cp /workspace {file_name.replace('.java', '')}"
            ]
        else:
            # For Python, the Docker image should contain Python
            docker_command = [
                "docker", "run", "--rm", 
                "-v", f"{temp_dir}:/workspace", 
                docker_image, "python", f"/workspace/{file_name}"
            ]
        
        # Run the Docker command
        print("start_running")
        run_result = subprocess.run(docker_command, capture_output=True, text=True)
        
        if run_result.returncode == 0:
            return run_result.stdout, run_result.returncode
        else:
            return run_result.stderr, run_result.returncode

def processing_tasks(code, language, task,user_prompt):

    fixed_promt = (
        "Please provide the following in response to the user's request:\n"
        "1. The executable code remove all comments(Be aware of the infinite loop and memory leak)\n"
        "2. The programming language of the code in all lowercase letters\n"
        "3. Find the name of the Docker image in Docker Hub that can run the code you return, with the version if specified by the user's prompt or comments in code I provided"
        "(otherwise, use the latest executable version available).\n"
        "4. The public class name of Java code,If the code language you return is python just return the word : output\n"
        "The format of the response should only be json and inluding(code, language, docker_image,class_name)"
    )

    if task[0] == 'B':
        # result = run_code(code, language)
        dev_prompt = (
            f"The following {language} code contains an error. Fix it so that it can runs successfully.\n\n"
            f"Code:\n{code}\n\n"
            # f"Error:\n{result}\n\n"
            f"{fixed_promt}"
        )
    else:
        if task[1] == '1':
            if language == "python":
                dev_prompt = (
                    "Convert the following Python code to other version(Refer to the comments in the code ) of Python."
                    "Ensure that all features unsupported are correctly refactored. "  
                    "Generate an executable Python script and ensure the execution result is the same as the original. "
                    "Don't need to determine the version in the code.\n\n"
                    f"Code:\n{code}\n\n"
                    f"{fixed_promt}"
                )
            elif language == "java":
                dev_prompt = (
                    "Convert the following Java code to other version of Java(Refer to the comments in the code ) "
                    "Ensure that all features unsupported are correctly refactored. "
                    "Generate an executable Java script and ensure the execution result is the same as the original. "
                    "Don't need to  determine the version in the code.\n\n"
                    f"Code:\n{code}\n\n"
                    f"{fixed_promt}"
                )
        elif task[1] == '2':
            if language == "python":
                dev_prompt = (
                    "Convert the following Python code to Java while preserving its logic and functionality. "
                    "Ensure that all Python-specific constructs are properly adapted to Java idioms.\n\n"
                    f"Code:\n{code}\n\n"
                    f"{fixed_promt}"
                )
            elif language == "java":
                dev_prompt = (
                    "Convert the following Java code to Python while preserving its logic and functionality. "
                    "Ensure that all Java-specific constructs are properly adapted to Python idioms. "
                    f"Code:\n{code}\n\n"
                    f"{fixed_promt}"
                )
        elif task[1] == '3':
            dev_prompt = (
                f"Optimize the following {language} code for better efficiency "
                "(such as reducing time or space complexity) while maintaining its functionality. "
                "Refer to the comments in the code if you need them.\n\n"
                f"Code:\n{code}\n\n"
                f"{fixed_promt}"
            )

    response_text = OpenAIChat.chat(dev_prompt,user_prompt)
    response_json = re.sub(r"```(?:\w+)?\n?", "", response_text).strip("`")
    return response_json

def fix_code_with_llm(response_json, error_message,usr_prompt):


    response_dict = json.loads(response_json)  
    code = response_dict["code"]
    language = response_dict["language"]

    fixed_promt = (
        "Please provide the following in response to the user's request:\n"
        "1. The executable code remove all comments(Be aware of the infinite loop and memory leak)\n"
        "2. The programming language of the code in all lowercase letters\n"
        "3. Find the name of the Docker image in Docker Hub that can run the code you return, with the version if specified by the user's prompt or comments in code I provided"
        "(otherwise, use the latest executable version available).\n"
        "4. The public class name of Java code,If the code language you return is python just return the word : output\n"
        "The format of the response should only be json and inluding(code, language, docker_image,class_name)"
    )

    prompt = (
        f"This {language} code contains an error. Please help me fix it.\n\n"
        f"Code:\n{code}\n\n"
        f"Error:\n{error_message}\n\n"
        f"{fixed_promt}"
        
    )

    response_text = OpenAIChat.chat(prompt,usr_prompt)
    response_json = re.sub(r"```(?:\w+)?\n?", "", response_text).strip("`")
    return response_json

def return_code_response(code_response,response_json,result,status):
    response_dict = json.loads(response_json)  
    code = response_dict["code"]
    language = response_dict["language"]
    java_class_name = response_dict["class_name"]
    docker_image = response_dict["docker_image"]

    code_response.file = code
    if language == "java":
        code_response.filename = java_class_name + ".java"
    else:
        code_response.filename = "output.py"
    if status == 0:
        code_response.success_msg = result
        code_response.status = True
    else:
        code_response.error_msg = result
        code_response.status = False
    # subprocess.run(f"docker rmi -f $(docker images --filter=reference='{docker_image}' -q)", shell=True)
    subprocess.run(f"docker rmi -f $(docker images -q)", shell=True)
    return code_response


def StartProcess(code, task, usr_prompt):
    
    count = 0
    
    code_response = CodeResponse(file="", filename="", success_msg="", error_msg="", status=False)

    language = detect_language(code)
    if language == "unknown":
        code_response.error_msg = "Could not determine the programming language."
        code_response.status = False
        return code_response
    else:

        response_json = processing_tasks(code, language, task,usr_prompt)

        result,status = run_code(response_json)
        
    
        print("result:",result,"status:",status)

        while status  == 1 and count < 3:
            count += 1
            print("Fixing error...")
            response_json = fix_code_with_llm(response_json,result,usr_prompt)
            result,status = run_code(response_json)
        
        return return_code_response(code_response,response_json,result,status)



if __name__ == "__main__":
    count = 0
    input_file_path = "./TestCase/A1-2.py"  # Path to the code file
    usr_prompt = "Help me change the code to Python 2.7 compatible."
    with open(input_file_path, "r") as file:
        code = file.read()

    language = detect_language(code)
    if language == "unknown":
        print("Could not determine the programming language.")
    else:
        task = input("Please enter the task:")

        response_json = processing_tasks(code, language, task,usr_prompt)

        
        result,status = run_code(response_json)
        
    
        print("result:",result,"status:",status)

        while status  == 1 and count < 3:
            count += 1
            print("Fixing error...")
            response_json = fix_code_with_llm(response_json,result,usr_prompt)
            result,status = run_code(response_json)

         
        print("Execution Result:\n", result)

