import os
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

# Item ID : quantity available
inventory = {"keyboard": 10, "mouse": 25, "monitor": 3}
delay = int(os.getenv("INVENTORY_DELAY_SECONDS", "0"))


@app.get("/health")
def health():
    return jsonify(service="rest-inventory", status="ok")


@app.post("/inventory/check")
def check_inventory():
    payload = request.get_json(silent=True) or {}
    item_id = payload.get("item_id")
    quantity = payload.get("quantity")

    if not isinstance(item_id, str) or not isinstance(quantity, int) or quantity <= 0:
        return jsonify(error="item_id must be a string and quantity must be a positive integer"), 400

    # Used only when testing timeout handling.
    if delay > 0:
        time.sleep(delay)

    available_quantity = inventory.get(item_id, 0)
    available = available_quantity >= quantity

    return jsonify(item_id=item_id, requested_quantity=quantity, available_quantity=available_quantity, available=available)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
