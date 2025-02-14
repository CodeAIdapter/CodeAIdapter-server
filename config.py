import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GCP_CREDENTIALS = os.environ.get("GCP_CREDENTIALS")
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    GCP_CLUSTER_NAME = os.environ.get("GCP_CLUSTER_NAME")
    GCP_CLUSTER_ZONE = os.environ.get("GCP_CLUSTER_ZONE")
    GCP_ARTIFACT_REGISTRY = os.environ.get("GCP_ARTIFACT_REGISTRY")
    GCP_ARTIFACT_REGISTRY_REPO = os.environ.get("GCP_ARTIFACT_REGISTRY_REPO")