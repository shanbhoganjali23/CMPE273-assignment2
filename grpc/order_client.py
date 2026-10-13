"""gRPC Order client used to demonstrate the Order Service."""

import argparse
import grpc
import inventory_pb2
import inventory_pb2_grpc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--item-id", default="keyboard")
    parser.add_argument("--quantity", type=int, default=2)
    args = parser.parse_args()
    with grpc.insecure_channel("127.0.0.1:50052") as channel:
        stub = inventory_pb2_grpc.OrderServiceStub(channel)
        try:
            response = stub.PlaceOrder(inventory_pb2.OrderRequest(item_id=args.item_id, quantity=args.quantity), timeout=4)
            print(f"SUCCESS: item_id={response.item_id} quantity={response.quantity} status={response.status}")
        except grpc.RpcError as error:
            print(f"ERROR: code={error.code().name} details={error.details()}")


if __name__ == "__main__":
    main()
