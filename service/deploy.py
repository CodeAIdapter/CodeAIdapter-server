from kubernetes import client, config
from pathlib import Path
import yaml
import tempfile
from typing import Dict, Optional

class K8sService:
    def __init__(self):
        config.load_kube_config()
        self.api = client.ApiClient()
        self.k8s_client = client.CustomObjectsApi()

    def create_deployment_config(self, 
                               service_name: str,
                               image: str,
                               replicas: int = 1,
                               port: int = 80,
                               resources: Optional[Dict] = None) -> Dict:
        """Create K8s deployment configuration"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_name
            },
            "spec": {
                "replicas": replicas,
                "selector": {"matchLabels": {"app": service_name}},
                "template": {
                    "metadata": {"labels": {"app": service_name}},
                    "spec": {
                        "containers": [{
                            "name": service_name,
                            "image": image,
                            "ports": [{"containerPort": port}],
                            "resources": resources or {
                                "limits": {
                                    "cpu": "500m",
                                    "memory": "512Mi"
                                },
                                "requests": {
                                    "cpu": "200m",
                                    "memory": "256Mi"
                                }
                            }
                        }]
                    }
                }
            }
        }

    def deploy(self, yaml_content: Dict) -> bool:
        """Deploy to Kubernetes cluster"""
        try:
            # Write config to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
                yaml.dump(yaml_content, tmp)
                tmp.flush()
                
                # Apply configuration
                result = client.AppsV1Api(self.api).create_namespaced_deployment(
                    body=yaml_content,
                    namespace="default"
                )
                return True if result else False
        except Exception as e:
            print(f"Deployment error: {str(e)}")
            return False

    def delete_deployment(self, name: str, namespace: str = "default") -> bool:
        """Delete a deployment"""
        try:
            client.AppsV1Api(self.api).delete_namespaced_deployment(
                name=name,
                namespace=namespace
            )
            return True
        except Exception as e:
            print(f"Deletion error: {str(e)}")
            return False
