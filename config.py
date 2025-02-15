import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """
    Configuration class to hold environment variables for the application.
    """
    GCP_CREDENTIALS = os.environ.get("GCP_CREDENTIALS")  # Path to GCP credentials JSON file
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")  # GCP project ID
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # OpenAI API key
    GCP_CLUSTER_NAME = os.environ.get("GCP_CLUSTER_NAME")  # GCP Kubernetes cluster name
    GCP_CLUSTER_ZONE = os.environ.get("GCP_CLUSTER_ZONE")  # GCP Kubernetes cluster zone
    GCP_ARTIFACT_REGISTRY = os.environ.get("GCP_ARTIFACT_REGISTRY")  # GCP Artifact Registry URL
    GCP_ARTIFACT_REGISTRY_REPO = os.environ.get("GCP_ARTIFACT_REGISTRY_REPO")  # GCP Artifact Registry repository name
