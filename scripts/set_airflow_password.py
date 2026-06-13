import json
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Airflow's simple_auth_manager reads credentials from this generated file at startup
PASSWORDS_FILE = "/opt/airflow/simple_auth_manager_passwords.json.generated"
ADMIN_USER = os.getenv("AIRFLOW_ADMIN_USER")
ADMIN_PASSWORD = os.getenv("AIRFLOW_ADMIN_PASSWORD")

json.dump({ADMIN_USER: ADMIN_PASSWORD}, open(PASSWORDS_FILE, "w"))
print(f"Airflow password set -> {PASSWORDS_FILE}")
