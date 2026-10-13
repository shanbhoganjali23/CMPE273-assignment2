import os
import time
from concurrent import futures

import grpc
import inventory_pb2
import inventory_pb2_grpc

inventory = {"keyboard": 10, "mouse": 25, "monitor": 3}
delay = int(os.getenv("INVENTORY_DELAY_SECONDS", "0"))


class InventoryService(inventory_pb2_grpc.InventoryServiceServicer):
    def CheckInventory(self, request, context):
        if not request.item_id or request.quantity <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "item_id and positive quantity are required")
        # Used only when testing the deadline.
        if delay > 0:
            time.sleep(delay)

        available_quantity = inventory.get(request.item_id, 0)
        if available_quantity < request.quantity:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, f"Requested {request.quantity}; only {available_quantity} available for {request.item_id}")

        return inventory_pb2.InventoryResponse(item_id=request.item_id, requested_quantity=request.quantity, available_quantity=available_quantity, available=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Inventory Service running on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
