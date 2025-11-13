# orders/main.py
import asyncio
import grpc
from datetime import datetime, timezone

from db_handler import DBHandler
from menu import get_items_with_details
import orders_pb2, orders_pb2_grpc

from google.protobuf.timestamp_pb2 import Timestamp
import uuid

class OrdersServicer(orders_pb2_grpc.OrdersServicer):
    def __init__(self):
        self.db_handler = DBHandler()

    async def CreateOrder(self, request, context):
        try:
            items = get_items_with_details(request.items)
        except Exception as e:
            print(f"Database error: {e}")
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Invalid items in order: {str(e)}"
            )

        # Build order doc
        order_id = str(uuid.uuid4())
        doc = {
            "_id": order_id,
            "order_id": order_id,
            "customer_id": request.customer_id,
            "items": items,
            "status": "created",
            "payment_link": "",
            "created_at": datetime.now(timezone.utc)
        }

        try:
            await self.db_handler.create_order(doc)
        except Exception as e:
            print(f"Database error: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to create order: {str(e)}"
            )

        ts = Timestamp()
        ts.FromDatetime(doc["created_at"])
        return orders_pb2.Order(
            order_id=doc["order_id"],
            customer_id=doc["customer_id"],
            items=doc.get("items", []),
            status=doc.get("status", ""),
            payment_link=doc.get("payment_link", ""),
            created_at=ts
        )

    async def GetOrder(self, request, context):
        doc = await self.db_handler.get_order(request.order_id, request.customer_id)

        if not doc:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            return orders_pb2.Order()
        
        ts = Timestamp()
        ts.FromDatetime(doc["created_at"])
        return orders_pb2.Order(
            order_id=doc["order_id"],
            customer_id=doc["customer_id"],
            items=doc.get("items", []),
            status=doc.get("status", ""),
            payment_link=doc.get("payment_link", ""),
            created_at=ts
        )

async def serve():
    server = grpc.aio.server()
    orders_pb2_grpc.add_OrdersServicer_to_server(OrdersServicer(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    print(f"gRPC server starting on {listen_addr}")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
