# gateway/main.py
import grpc
import orders_pb2, orders_pb2_grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from google.protobuf.json_format import MessageToDict

app = FastAPI(title="Gateway")

GRPC_TARGET = "orders:50051"

# Reuse a single channel/stub
_channel = None
_stub = None

def get_stub():
    global _channel, _stub
    if _stub is None:
        _channel = grpc.aio.insecure_channel(GRPC_TARGET)
        _stub = orders_pb2_grpc.OrdersStub(_channel)
    return _stub

class CreateOrderModel(BaseModel):
    items: list[str]
    total: float

@app.post("/api/customers/{customer_id}/orders")
async def create_order(customer_id: str, body: CreateOrderModel):
    stub = get_stub()
    req = orders_pb2.CreateOrderRequest(customer_id=customer_id, items=body.items, total=body.total)
    try:
        resp = await stub.CreateOrder(req, timeout=5)
        return {"order_id": resp.order_id, "status": resp.status}
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/orders/{order_id}")
async def get_order(customer_id: str, order_id: str):
    stub = get_stub()
    req = orders_pb2.GetOrderRequest(customer_id=customer_id, order_id=order_id)
    try:
        resp = await stub.GetOrder(req, timeout=5)
        # convert protobuf to dict
        out = MessageToDict(resp, including_default_value_fields=True, preserving_proto_field_name=True)
        # Basic check for empty/order not found
        if not resp.order_id:
            raise HTTPException(status_code=404, detail="Order not found")
        return out
    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=e.details())
        raise HTTPException(status_code=500, detail=str(e))
