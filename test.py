from service.deploy import deploy_handle
from utils import CodeResponse
import os
import sys

def main():
    args = sys.argv[1:]
    filename = args[0]
    prompt = args[1]
    response = deploy_handle(prompt, os.path.basename(filename), open(filename, "r").read())
    print("=== File ===")
    print(response.file)
    print("=== Filename ===")
    print(response.filename)
    print("=== Success Message ===")
    print(response.success_msg)
    print("=== Error Message ===")
    print(response.error_msg)
    print("=== Status ===")
    print(response.status)

if __name__ == "__main__":
    main()