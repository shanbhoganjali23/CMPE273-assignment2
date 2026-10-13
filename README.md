# CMPE 273 Assignment 2 - REST and gRPC

For this assignment, I made an Order Service and an Inventory Service. I implemented the communication between them in two ways: REST and gRPC.

The inventory used in both versions is:

```text
keyboard: 10
mouse: 25
monitor: 3
```

## Setup

From the main project folder, run these commands once:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## REST version

For REST, the Inventory Service runs on port 5001 and the Order Service runs on port 5000.

Open two terminals. In both terminals, go to the project folder and activate the virtual environment.

```bash
source .venv/bin/activate
```

In the first terminal, start Inventory Service:

```bash
cd rest
python inventory_service.py
```

In the second terminal, start Order Service:

```bash
cd rest
python order_service.py
```

### Successful REST request

```bash
curl -i -X POST http://127.0.0.1:5000/orders \
  -H 'Content-Type: application/json' \
  -d '{"item_id":"keyboard","quantity":2}'
```

I got a `201 CREATED` response.

```json
{"item_id":"keyboard","message":"Order placed successfully","quantity":2}
```

### Item not available

```bash
curl -i -X POST http://127.0.0.1:5000/orders \
  -H 'Content-Type: application/json' \
  -d '{"item_id":"monitor","quantity":10}'
```

There are only three monitors in inventory, so this returns `409 CONFLICT`.

### REST timeout

I used a two-second timeout in Order Service. To make Inventory Service respond slowly, I restarted it with a five-second delay:

```bash
INVENTORY_DELAY_SECONDS=5 python inventory_service.py
```

Then I sent the same successful-order request again. Order Service returned `504 GATEWAY TIMEOUT`:

```json
{"error":"Inventory Service timed out; please try again"}
```

Order Service was still running after the timeout:

```bash
curl http://127.0.0.1:5000/health
```

```json
{"service":"rest-order","status":"ok"}
```

## gRPC version

The gRPC Inventory Service runs on port 50051 and the gRPC Order Service runs on port 50052.

The generated protobuf files are already included in this repository. If they need to be generated again, run this from the `grpc` folder:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inventory.proto
```

Open three terminals and activate the virtual environment in each one.

Start gRPC Inventory Service:

```bash
cd grpc
python inventory_server.py
```

Start gRPC Order Service in another terminal:

```bash
cd grpc
python order_service.py
```

Use this command in the third terminal to place an order:

```bash
cd grpc
python order_client.py --item-id keyboard --quantity 2
```

Example successful output:

```text
SUCCESS: item_id=keyboard quantity=2 status=created
```

For an unavailable item, I used this command:

```bash
python order_client.py --item-id monitor --quantity 10
```

It returns this gRPC error:

```text
ERROR: code=FAILED_PRECONDITION details=Requested 10; only 3 available for monitor
```

### gRPC deadline

I used a two-second deadline for the Order Service call to Inventory Service. I restarted the Inventory Service with a five-second delay:

```bash
INVENTORY_DELAY_SECONDS=5 python inventory_server.py
```

Then I ran:

```bash
python order_client.py --item-id keyboard --quantity 2
```

The result was:

```text
ERROR: code=DEADLINE_EXCEEDED details=Inventory deadline exceeded; please try again
```

I then restarted Inventory Service normally and ran the client again. It worked without restarting the gRPC Order Service, so the Order Service remained running after the deadline error.

## REST and gRPC comparison

I found REST easier to test because I could use `curl` and directly see the JSON response. For gRPC, I had to create the proto file and generate the Python files first, so setup took a little more work. But gRPC made the request and response format clearer because they were defined in the proto contract. When I added a delay to Inventory, REST returned a timeout error and gRPC returned `DEADLINE_EXCEEDED`. In both cases, the Order Service kept running and could process requests again after Inventory was available.
