from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
NAVBLUE_URL = os.getenv("NAVBLUE_URL")