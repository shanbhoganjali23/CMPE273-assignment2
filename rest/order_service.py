import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

inventory_url = os.getenv("INVENTORY_URL", "http://127.0.0.1:5001/inventory/check")
timeout = 2


@app.get("/health")
def health():
    return jsonify(service="rest-order", status="ok")


@app.post("/orders")
def create_order():
    payload = request.get_json(silent=True) or {}
    item_id = payload.get("item_id")
    quantity = payload.get("quantity")

    if not isinstance(item_id, str) or not isinstance(quantity, int) or quantity <= 0:
        return jsonify(error="item_id must be a string and quantity must be a positive integer"), 400

    try:
        response = requests.post(inventory_url, json={"item_id": item_id, "quantity": quantity}, timeout=timeout)
        response.raise_for_status()
        inventory = response.json()
    except requests.Timeout:
        return jsonify(error="Inventory Service timed out; please try again"), 504
    except requests.RequestException:
        return jsonify(error="Inventory Service is unavailable"), 503

    if not inventory["available"]:
        return jsonify(error="Requested item quantity is unavailable"), 409

    return jsonify(message="Order placed successfully", item_id=item_id, quantity=quantity), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
