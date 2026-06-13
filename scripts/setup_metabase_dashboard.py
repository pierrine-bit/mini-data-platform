import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

METABASE_URL = "http://localhost:3001"
EMAIL = os.getenv("METABASE_EMAIL", "nkurangapierrine@gmail.com")
PASSWORD = os.getenv("METABASE_PASSWORD", "Metabase@2026")

session = requests.Session()


def wait_for_metabase():
    log.info("Connecting to Metabase...")
    for _ in range(30):
        try:
            res = requests.get(f"{METABASE_URL}/api/health", timeout=5)
            if res.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(5)
    raise Exception("Metabase did not become ready in time.")


def setup_metabase():
    props = requests.get(f"{METABASE_URL}/api/session/properties").json()
    setup_token = props.get("setup-token")
    if not setup_token:
        return
    log.info("Running first-time setup...")
    payload = {
        "token": setup_token,
        "user": {
            "first_name": "Pierrine",
            "last_name": "M.nkuranga",
            "email": EMAIL,
            "password": PASSWORD,
            "site_name": "Mini Data Platform",
        },
        "prefs": {"site_name": "Mini Data Platform", "allow_tracking": False},
    }
    res = requests.post(f"{METABASE_URL}/api/setup", json=payload)
    if res.status_code == 403:
        return
    res.raise_for_status()
    log.info("Setup complete.")


def login():
    res = session.post(f"{METABASE_URL}/api/session", json={"username": EMAIL, "password": PASSWORD})
    res.raise_for_status()
    token = res.json()["id"]
    session.headers.update({"X-Metabase-Session": token})


def get_or_create_database():
    res = session.get(f"{METABASE_URL}/api/database")
    res.raise_for_status()
    for db in res.json()["data"]:
        if "Mini Data Platform" in db["name"]:
            return db["id"]
    log.info("Connecting database...")
    payload = {
        "name": "Mini Data Platform",
        "engine": "postgres",
        "details": {
            "host": "postgres",
            "port": 5432,
            "dbname": "airflow",
            "user": "airflow",
            "password": "airflow",
            "schema-filters-type": "all",
            "ssl": False,
        },
    }
    res = session.post(f"{METABASE_URL}/api/database", json=payload)
    res.raise_for_status()
    log.info("Database connected. Waiting for sync...")
    time.sleep(10)
    return res.json()["id"]


def get_table_id(db_id):
    res = session.get(f"{METABASE_URL}/api/database/{db_id}/metadata")
    res.raise_for_status()
    for table in res.json()["tables"]:
        if table["name"].lower() == "sales":
            return table["id"]
    raise Exception("Sales table not found.")


def get_field_ids(table_id):
    res = session.get(f"{METABASE_URL}/api/table/{table_id}/query_metadata")
    res.raise_for_status()
    fields = {}
    for f in res.json()["fields"]:
        fields[f["name"]] = f["id"]
    return fields


def create_question(name, dataset_query, display, visualization_settings=None):
    payload = {
        "name": name,
        "dataset_query": dataset_query,
        "display": display,
        "visualization_settings": visualization_settings or {},
    }
    res = session.post(f"{METABASE_URL}/api/card", json=payload)
    res.raise_for_status()
    return res.json()["id"]


def cleanup_duplicates():
    res = session.get(f"{METABASE_URL}/api/card")
    res.raise_for_status()
    seen = {}
    deleted = 0
    for card in res.json():
        name = card["name"]
        if name in seen:
            session.delete(f"{METABASE_URL}/api/card/{card['id']}")
            deleted += 1
        else:
            seen[name] = card["id"]
    if deleted:
        log.info(f"Cleaned up {deleted} duplicate questions.")


def delete_existing_dashboards(name):
    res = session.get(f"{METABASE_URL}/api/dashboard")
    res.raise_for_status()
    for dash in res.json():
        if dash.get("name") == name:
            session.delete(f"{METABASE_URL}/api/dashboard/{dash['id']}")


def create_dashboard(name):
    delete_existing_dashboards(name)
    res = session.post(f"{METABASE_URL}/api/dashboard", json={"name": name})
    res.raise_for_status()
    return res.json()["id"]


def add_all_cards_to_dashboard(dashboard_id, cards):
    payload = {"cards": cards}
    res = session.put(f"{METABASE_URL}/api/dashboard/{dashboard_id}/cards", json=payload)
    res.raise_for_status()


def main():
    wait_for_metabase()
    setup_metabase()
    login()
    cleanup_duplicates()

    db_id = get_or_create_database()
    table_id = get_table_id(db_id)
    fields = get_field_ids(table_id)

    amount_id = fields["amount"]
    region_id = fields["region"]
    product_id = fields["product"]
    order_date_id = fields["order_date"]

    log.info("Building questions...")

    total_sales_id = create_question(
        "Total Sales",
        {
            "type": "query",
            "database": db_id,
            "query": {
                "source-table": table_id,
                "aggregation": [["sum", ["field", amount_id, None]]],
            },
        },
        "scalar",
        {"scalar.prefix": "$"},
    )

    total_orders_id = create_question(
        "Total Orders",
        {
            "type": "query",
            "database": db_id,
            "query": {
                "source-table": table_id,
                "aggregation": [["count"]],
            },
        },
        "scalar",
    )

    avg_order_id = create_question(
        "Average Order Value",
        {
            "type": "query",
            "database": db_id,
            "query": {
                "source-table": table_id,
                "aggregation": [["avg", ["field", amount_id, None]]],
            },
        },
        "scalar",
        {"scalar.prefix": "$"},
    )

    top_region_id = create_question(
        "Top Performing Region",
        {
            "type": "query",
            "database": db_id,
            "query": {
                "source-table": table_id,
                "aggregation": [["sum", ["field", amount_id, None]]],
                "breakout": [["field", region_id, None]],
                "order-by": [["desc", ["aggregation", 0]]],
            },
        },
        "bar",
        {
            "graph.colors": ["#84BB4C"],
            "graph.x_axis.title_text": "Region",
            "graph.y_axis.title_text": "Sum of Amount",
        },
    )

    top_product_id = create_question(
        "Top Selling Product",
        {
            "type": "query",
            "database": db_id,
            "query": {
                "source-table": table_id,
                "aggregation": [["sum", ["field", amount_id, None]]],
                "breakout": [["field", product_id, None]],
                "order-by": [["desc", ["aggregation", 0]]],
            },
        },
        "bar",
        {
            "graph.colors": ["#84BB4C"],
            "graph.x_axis.title_text": "Product",
            "graph.y_axis.title_text": "Sum of Amount",
        },
    )

    monthly_trend_id = create_question(
        "Monthly Sales Trend",
        {
            "type": "query",
            "database": db_id,
            "query": {
                "source-table": table_id,
                "aggregation": [["sum", ["field", amount_id, None]]],
                "breakout": [["field", order_date_id, {"temporal-unit": "month"}]],
                "order-by": [["asc", ["breakout", 0]]],
            },
        },
        "line",
        {"graph.colors": ["#84BB4C"]},
    )

    product_share_id = create_question(
        "Product Sales Share",
        {
            "type": "query",
            "database": db_id,
            "query": {
                "source-table": table_id,
                "aggregation": [["sum", ["field", amount_id, None]]],
                "breakout": [["field", product_id, None]],
            },
        },
        "pie",
    )


    dash_id = create_dashboard("Sales Performance Dashboard")

    key_insights = (
        "## Key Insights\n"
        "- Monitor total revenue, order volume, and average order value at a glance\n"
        "- Compare regional and product performance with bar charts\n"
        "- Track revenue trends over time and customer concentration\n"
        "- Use the monthly trend to spot seasonality and growth patterns"
    )

    cards = [
        {
            "id": -1,
            "card_id": None,
            "col": 0, "row": 0, "size_x": 18, "size_y": 3,
            "visualization_settings": {
                "virtual_card": {"display": "text", "visualization_settings": {}, "dataset_query": {}},
                "text": key_insights,
            },
        },
        {"id": -2,  "card_id": total_sales_id,     "col": 0,  "row": 3,  "size_x": 6, "size_y": 3, "visualization_settings": {}},
        {"id": -3,  "card_id": total_orders_id,    "col": 6,  "row": 3,  "size_x": 6, "size_y": 3, "visualization_settings": {}},
        {"id": -4,  "card_id": avg_order_id,       "col": 12, "row": 3,  "size_x": 6, "size_y": 3, "visualization_settings": {}},
        {"id": -5,  "card_id": top_region_id,      "col": 0,  "row": 6,  "size_x": 9, "size_y": 5, "visualization_settings": {}},
        {"id": -6,  "card_id": top_product_id,     "col": 9,  "row": 6,  "size_x": 9, "size_y": 5, "visualization_settings": {}},
        {"id": -7,  "card_id": monthly_trend_id,   "col": 0,  "row": 11, "size_x": 9, "size_y": 5, "visualization_settings": {}},
        {"id": -8,  "card_id": product_share_id,   "col": 9,  "row": 11, "size_x": 9, "size_y": 5, "visualization_settings": {}},
    ]

    add_all_cards_to_dashboard(dash_id, cards)
    log.info(f"Done! Open your dashboard at: {METABASE_URL}/dashboard/{dash_id}")


if __name__ == "__main__":
    main()
