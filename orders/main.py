# orders/main.py
import asyncio
import os
import grpc
from datetime import datetime, timezone

import orders_pb2, orders_pb2_grpc

from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import Parse, ParseDict
import uuid

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
RABBIT_URI = os.getenv("RABBIT_URI", "amqp://guest:guest@rabbitmq/")

class OrdersServicer(orders_pb2_grpc.OrdersServicer):
    async def CreateOrder(self, request, context):
        items = [{
            "item_id": item.item_id,
            "name": "name_placeholder",
            "quantity": item.quantity,
            "price": 10
        } for item in request.items]

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
        doc = {
            "_id": request.order_id,
            "order_id": request.order_id,
            "customer_id": request.customer_id,
            "items": [],
            "status": "created",
            "payment_link": "",
            "created_at": datetime.now(timezone.utc)
        }

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
