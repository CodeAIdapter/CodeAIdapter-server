import os
import uuid
import time
from typing import Optional, List
from contextlib import contextmanager

import pexpect

from config import Config
from utils import CodeResponse
from .utils import (
    code_extract,
    generate_dockerfile,
    generate_config_yaml,
    generate_report
)

SAVE_DIR = "tmp"
DEFAULT_DOCKERFILE = "Dockerfile"
DEFAULT_CONFIG_YAML = "config.yaml"
TIMEOUT = 120

@contextmanager
def change_dir(path: str):
    """
    Context manager to change the current working directory and then restore it.
    """
    original_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_dir)

def deploy_handle(prompt: str, filename: str, file_content: str) -> CodeResponse:
    """
    Handle deployment request:
      1. Extract code content from the file.
      2. Generate a Dockerfile and a Kubernetes deployment config.yaml.
      3. Build and push the Docker image, then deploy it.
      4. Generate a deployment report.

    Args:
        prompt (str): Deployment prompt message.
        filename (str): The name of the file containing the code.
        file_content (str): The content of the file.

    Returns:
        CodeResponse: A response object containing deployment status, logs, and file information.
    """
    service_name = f"codeaidapter-{uuid.uuid4()}"  # Unique service name using UUID

    # Extract code content (can be further customized by the extraction function)
    code_content = code_extract(filename=filename, code_content=file_content)
    dockerfile_content = generate_dockerfile(filename=filename, code_content=code_content, prompt=prompt)
    config_yaml_content = generate_config_yaml(
        docker_image_tag=f"{Config.GCP_ARTIFACT_REGISTRY}/{Config.GCP_PROJECT_ID}/{Config.GCP_ARTIFACT_REGISTRY_REPO}/{service_name}:latest",
        dockerfile_content=dockerfile_content,
        pod_name=service_name,
        prompt=prompt
    )
    
    # Create a Kubernetes service and perform deployment
    service = K8sService(
        service_name=service_name,
        code_filename=filename,
        code_content=file_content,
        dockerfile_content=dockerfile_content,
        config_yaml_content=config_yaml_content
    )
    status = service.run()
    # import objprint
    # with open('run.log', 'w') as f:
    #     f.write(objprint.objstr(service))

    # Generate a deployment report
    report = generate_report(
        dockerfile_content=dockerfile_content,
        config_yaml_content=config_yaml_content,
        logs=service.logs
    )
    success_msg = report if status else None
    error_msg = report if not status else None

    return CodeResponse(
        file=service.config_yaml_content,
        filename=os.path.basename(service.config_yaml),
        success_msg=success_msg,
        error_msg=error_msg,
        status=status
    )

class K8sService:
    def __init__(
        self,
        service_name: str,
        code_filename: str,
        code_content: str,
        dockerfile_content: str,
        config_yaml_content: str,
    ):
        """
        Initialize the Kubernetes service by writing the code file, Dockerfile, and config.yaml 
        into a dedicated service directory.

        Args:
            service_name (str): The unique name of the service.
            code_filename (str): The name of the code file.
            code_content (str): The content of the code file.
            dockerfile_content (str): The content of the Dockerfile.
            config_yaml_content (str): The content of the Kubernetes deployment config.yaml.
        """
        self.service_name = service_name
        self.code_filename = code_filename
        self.code_content = code_content
        self.dockerfile_content = dockerfile_content
        self.config_yaml_content = config_yaml_content

        # Create the service directory (intermediate directories will be created if missing)
        self.service_dir = os.path.join(SAVE_DIR, self.service_name)
        os.makedirs(self.service_dir, exist_ok=True)

        # Write the Dockerfile
        self.dockerfile = os.path.join(self.service_dir, DEFAULT_DOCKERFILE)
        with open(self.dockerfile, "w", encoding="utf-8") as f:
            f.write(self.dockerfile_content)
        
        # Write the config.yaml file
        self.config_yaml = os.path.join(self.service_dir, DEFAULT_CONFIG_YAML)
        with open(self.config_yaml, "w", encoding="utf-8") as f:
            f.write(self.config_yaml_content)

        # Write the code file
        with open(os.path.join(self.service_dir, self.code_filename), "w", encoding="utf-8") as f:
            f.write(self.code_content)

        self.logs: List[str] = []

    def _execute_command(self, command: str, max_size: Optional[int] = None) -> bool:
        """
        Execute a shell command using pexpect within the service directory and log its output.

        Args:
            command (str): The command to execute.

        Returns:
            bool: True if the command executes successfully; otherwise, False.
        """
        try:
            self.logs.append(f"Executing command: {command}")
            
            # Change to the service directory using the context manager
            with change_dir(self.service_dir):
                p = pexpect.spawn(command, encoding="utf-8", timeout=TIMEOUT)
                p.expect(pexpect.EOF)
                if max_size:
                    output = p.before[-max_size:]
                else:
                    output = p.before
                self.logs.append(f"Output:\n{output}")
                p.close()
                if p.exitstatus != 0:
                    self.logs.append(f"Error: Command '{command}' exited with status {p.exitstatus}")
                    return False
            return True

        except pexpect.TIMEOUT as e:
            self.logs.append(f"Command '{command}' timed out after {TIMEOUT}s: {str(e)}")
            return False
        except Exception as e:
            self.logs.append(f"Exception while executing command '{command}': {str(e)}")
            return False

    def __docker_push(self) -> bool:
        """
        Build, tag, and push the Docker image to the container registry.

        Returns:
            bool: True if all steps succeed; otherwise, False.
        """
        image_tag = f"{self.service_name}:latest"
        registry_tag = (
            f"{Config.GCP_ARTIFACT_REGISTRY}/"
            f"{Config.GCP_PROJECT_ID}/"
            f"{Config.GCP_ARTIFACT_REGISTRY_REPO}/{image_tag}"
        )
        commands = [
            f"sudo docker build --quiet -t {image_tag} .",
            f"sudo docker tag {image_tag} {registry_tag}",
            f"sudo docker push {registry_tag}"
        ]

        for cmd in commands:
            if not self._execute_command(cmd, max_size=500):
                self.logs.append(f"Failed executing: {cmd}")
                return False
        return True

    def __docker_deploy(self) -> bool:
        """
        Deploy the service using the generated Kubernetes config.yaml file.

        Returns:
            bool: True if the deployment is successful; otherwise, False.
        """
        # Apply the configuration first
        apply_cmd = f"kubectl apply -f {DEFAULT_CONFIG_YAML}"
        if not self._execute_command(apply_cmd):
            self.logs.append(f"Failed executing: {apply_cmd}")
            return False

        # Wait for the pod to appear (check up to 5 times, every 2 seconds)
        pod_found = False
        search_pod_name = ""
        for _ in range(15):
            # Use a bash shell to handle the pipe
            command = f"kubectl get pods | grep {self.service_name}"
            p = pexpect.spawn("/bin/bash", ["-c", command], encoding="utf-8")
            try:
                p.expect(pexpect.EOF, timeout=5)
            except pexpect.exceptions.TIMEOUT:
                p.close()
                time.sleep(2)
                continue

            output = p.before.strip()
            p.close()

            if output:
                # Check if the output contains "CrashLoopBackOff" or "Completed"
                if ("CrashLoopBackOff" in output) or ("Completed" in output):
                    pod_found = True
                    search_pod_name = output.split()[0]
                    self.logs.append(f"Pod {search_pod_name} found.")
                    break

            time.sleep(2)

        if not pod_found:
            self.logs.append(f"Search pod name: {search_pod_name} not found.")
            self.logs.append(f"Pod {self.service_name} not found.")
            return False

        # Now that the pod exists, retrieve its logs
        logs_cmd = f"kubectl logs {search_pod_name}"
        if not self._execute_command(logs_cmd):
            self.logs.append(f"Failed executing: {logs_cmd}")
            return False

        return True

    def run(self) -> bool:
        """
        Run the process to push the Docker image and deploy it on Kubernetes.

        Returns:
            bool: True if both push and deploy are successful; otherwise, False.
        """
        self.logs.append("Starting Docker push process...")
        if not self.__docker_push():
            self.logs.append("Docker push failed. Aborting deployment.")
            return False

        self.logs.append("Docker push successful. Starting deployment process...")
        if not self.__docker_deploy():
            self.logs.append("Deployment process failed.")
            return False

        self.logs.append("Deployment successful.")
        return True