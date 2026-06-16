import json
import logging
import os

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

PASSWORDS_FILE = "/opt/airflow/simple_auth_manager_passwords.json.generated"
ADMIN_USER = os.getenv("AIRFLOW_ADMIN_USER")
ADMIN_PASSWORD = os.getenv("AIRFLOW_ADMIN_PASSWORD")

with open(PASSWORDS_FILE, "w") as f:
    json.dump({ADMIN_USER: ADMIN_PASSWORD}, f)

logger.info("Airflow password file created at %s", PASSWORDS_FILE)