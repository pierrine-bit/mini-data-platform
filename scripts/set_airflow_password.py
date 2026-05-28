import json

PASSWORDS_FILE = "/opt/airflow/simple_auth_manager_passwords.json.generated"

json.dump({"admin": "admin"}, open(PASSWORDS_FILE, "w"))
print(f"Password set to 'admin' -> {PASSWORDS_FILE}")
