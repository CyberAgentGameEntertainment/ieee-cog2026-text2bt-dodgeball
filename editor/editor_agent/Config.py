import os
import pathlib
from dotenv import load_dotenv

dotenv_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path)

class Config:
    def __init__(self):
        self.PROJECT_DIRECTORY = pathlib.Path(os.getenv("PROJECT_DIRECTORY"))
        self.NEWNODE = os.getenv("NEWNODE", "true").lower() == "true"
        self.NEWBT = os.getenv("NEWBT", "true").lower() == "true"
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
        self.WAIT_UNITY = os.getenv("WAIT_UNITY", "false").lower() == "true"
        self.MODEL = os.getenv("MODEL", "gpt")

CONFIG = Config()
