# orders/main.py
import os
import asyncio
import grpc
from datetime import datetime, timezone

from db_handler import DBHandler
import orders_pb2, orders_pb2_grpc

from google.protobuf.timestamp_pb2 import Timestamp
import uuid

from google.protobuf.json_format import MessageToDict

STOCK_GRPC_TARGET = os.getenv("STOCK_GRPC_TARGET", "stock:2001")

# Reuse a single channel/stub
_channel = None
_stub = None

def get_stub():
    global _channel, _stub
    if _stub is None:
        _channel = grpc.aio.insecure_channel(STOCK_GRPC_TARGET)
        _stub = orders_pb2_grpc.StockStub(_channel)
    return _stub

class OrdersServicer(orders_pb2_grpc.OrdersServicer):
    def __init__(self):
        self.db_handler = DBHandler()

    async def CreateOrder(self, request, context):
        stub = get_stub()
        req = orders_pb2.CheckIfItemsInStockRequest(items=request.items)
        try:
            resp = await stub.CheckIfItemsInStock(req, timeout=5)
            resp = MessageToDict(resp, preserving_proto_field_name=True)
        except Exception as e:
            print(f"Stock service error: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to check stock service: {str(e)}"
            )

        if not resp.get("in_stock", False):
            await context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                "One or more items are out of stock"
            )
        items = resp.get("items", [])
        print(f"Items: {items}")

        # Build order doc
        order_id = str(uuid.uuid4())
        order = {
            "_id": order_id,
            "order_id": order_id,
            "customer_id": request.customer_id,
            "items": items,
            "status": "created",
            "payment_link": "",
            "created_at": datetime.now(timezone.utc)
        }

        try:
            await self.db_handler.create_order(order)
        except Exception as e:
            print(f"Database error: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to create order: {str(e)}"
            )

        ts = Timestamp()
        ts.FromDatetime(order["created_at"])
        return orders_pb2.Order(
            order_id=order["order_id"],
            customer_id=order["customer_id"],
            items=order.get("items", []),
            status=order.get("status", ""),
            payment_link=order.get("payment_link", ""),
            created_at=ts
        )

    async def GetOrder(self, request, context):
        try:
            order = await self.db_handler.get_order(request.order_id, request.customer_id)
        except Exception as e:
            print(f"Database error: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to get orders: {str(e)}"
            )

        if not order:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            return orders_pb2.Order()
        
        ts = Timestamp()
        ts.FromDatetime(order["created_at"])
        return orders_pb2.Order(
            order_id=order["order_id"],
            customer_id=order["customer_id"],
            items=order.get("items", []),
            status=order.get("status", ""),
            payment_link=order.get("payment_link", ""),
            created_at=ts
        )

async def serve():
    server = grpc.aio.server()
    orders_pb2_grpc.add_OrdersServicer_to_server(OrdersServicer(), server)
    listen_addr = "[::]:2000"
    server.add_insecure_port(listen_addr)
    print(f"gRPC server starting on {listen_addr}")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
