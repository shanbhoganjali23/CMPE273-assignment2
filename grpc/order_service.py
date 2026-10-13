import os
from concurrent import futures

import grpc
import inventory_pb2
import inventory_pb2_grpc

inventory_address = os.getenv("GRPC_INVENTORY_ADDRESS", "127.0.0.1:50051")
deadline = 2


class OrderService(inventory_pb2_grpc.OrderServiceServicer):
    def PlaceOrder(self, request, context):
        if not request.item_id or request.quantity <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "item_id and positive quantity are required")
        with grpc.insecure_channel(inventory_address) as channel:
            inventory_stub = inventory_pb2_grpc.InventoryServiceStub(channel)
            try:
                inventory_stub.CheckInventory(inventory_pb2.InventoryRequest(item_id=request.item_id, quantity=request.quantity), timeout=deadline)
            except grpc.RpcError as error:
                if error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Inventory deadline exceeded; please try again")
                if error.code() == grpc.StatusCode.FAILED_PRECONDITION:
                    context.abort(grpc.StatusCode.FAILED_PRECONDITION, error.details())
                context.abort(grpc.StatusCode.UNAVAILABLE, "Inventory Service is unavailable")
        return inventory_pb2.OrderResponse(item_id=request.item_id, quantity=request.quantity, status="created")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Order Service running on port 50052")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
