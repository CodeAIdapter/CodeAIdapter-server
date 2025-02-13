import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GCP_CREDENTIALS = os.environ.get("GCP_CREDENTIALS")
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")