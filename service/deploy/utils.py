from typing import List

from utils.llm import OpenAIChat

def code_extract(filename: str, code_content: str) -> str:        
    response = OpenAIChat.chat(
        dev_prompt="""
        Please only give me the code content from the source code.
        Don't include any comments or other information.
        Don't use Markdown or any other formatting.
        """,
        usr_prompt=f"""
        File: {filename}
        Code content: 
        {code_content}
        """
    )
    return response

def generate_dockerfile(
    filename: str,
    code_content: str,
    prompt: str = ""
) -> str:
    dockerfile_template = \
    """
    FROM <image>
    WORKDIR /app
    COPY <file> .
    RUN <command> # if needed
    CMD <command>
    """

    response = OpenAIChat.chat(
        dev_prompt=f"""
        I will give you source code content.
        Please give me Dockerfile content based on the code content.
        Don't include any comments or other information.
        Don't use Markdown or any other formatting.
        There is a template for Dockerfile:
        {dockerfile_template}
        """,
        usr_prompt=f"""
        File: {filename}
        Code content: 
        {code_content}
        --------------------------------
        {prompt}
        """
    )
    return response

def generate_config_yaml(
    docker_image_tag: str,
    dockerfile_content: str,
    pod_name: str,
    prompt: str = ""
) -> str:
    response = OpenAIChat.chat(
        dev_prompt="""
        I will give you with the content of the Dockerfile and its full name of Docker image that pushed to the registry and the pod name.
        Please give me the content of the config.yaml file based on the Dockerfile content and the pod name.
        Don't include any comments or other information.
        Don't use Markdown or any other formatting.
        """,
        usr_prompt=f"""
        Docker image tag: {docker_image_tag}
        Dockerfile content:
        {dockerfile_content}
        Pod name: {pod_name}
        --------------------------------
        {prompt}
        """
    )
    return response

def generate_deploy_command(
    config_yaml_content: str
) -> str:
    response = OpenAIChat.chat(
        dev_prompt="""
        I will give you with the content of the config.yaml file.
        Please give me the command to deploy the service based on the config.yaml content.
        And use `kubectl logs <pod-name>` in the end to get the logs.
        Don't include any comments or other information.
        Don't use Markdown or any other formatting.
        """,
        usr_prompt=f"""
        Config.yaml content:
        {config_yaml_content}
        """
    )
    return response

def generate_report(
    dockerfile_content: str,
    config_yaml_content: str,
    logs: List[str]
) -> str:
    log_str = "\n".join(logs)
    response = OpenAIChat.chat(
        dev_prompt="""
        I will give you with the content of the Dockerfile, the content of the config.yaml file, and the logs of the deployment.
        Please give me a report based on the Dockerfile content, the config.yaml content, and the logs.
        """,
        usr_prompt=f"""
        Dockerfile content:
        {dockerfile_content}
        Config.yaml content:
        {config_yaml_content}
        Logs:
        {log_str}
        """
    )
    return response