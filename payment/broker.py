import asyncio
import json
import os
import grpc
import orders_pb2_grpc, orders_pb2
from google.protobuf.json_format import MessageToDict
from aio_pika import connect, ExchangeType, Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage

ORDERS_GRPC_TARGET = os.getenv("ORDERS_GRPC_TARGET", "stock:2001")
RABBIT_URI = os.getenv("RABBIT_URI", "amqp://guest:guest@rabbitmq/")

# Reuse a single channel/stub
_channel = None
_stub = None

def get_stub():
    global _channel, _stub
    if _stub is None:
        _channel = grpc.aio.insecure_channel(ORDERS_GRPC_TARGET)
        _stub = orders_pb2_grpc.OrdersStub(_channel)
    return _stub

async def on_order_created(message: AbstractIncomingMessage) -> None:
    data = json.loads(message.body.decode())
    print(" [x] Received order.created:", data, flush=True)
    
    stub = get_stub()
    req = orders_pb2.Order(
        order_id=data["order_id"],
        status="waiting_payment",
        payment_link="http://example.com/pay",
    )
    try:
        resp = await stub.UpdateOrder(req, timeout=5)
        resp = MessageToDict(resp, preserving_proto_field_name=True)
        print(" [x] Updated order in order service:", resp, flush=True)
    except Exception as e:
        print(f"Order service error: {e}")

async def consume_order_created():
    # Perform connection
    connection = await connect(RABBIT_URI)
    async with connection:
        # Creating a channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue("order.created")

        # Start listening the queue with name 'order.created'
        await queue.consume(on_order_created, no_ack=True)

        print(" [*] Waiting for order created events.", flush=True)
        await asyncio.Future()

async def publish_order_paid(order_id: str):
    # Perform connection
    connection = await connect(RABBIT_URI)

    async with connection:
        # Creating a channel
        channel = await connection.channel()

        order_paid_exchange = await channel.declare_exchange(
            "order.paid", ExchangeType.FANOUT,
        )

        # Create JSON payload
        payload = {"order_id": order_id}
        message_body = json.dumps(payload).encode("utf-8")

        message = Message(
            message_body,
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        # Sending the message
        await order_paid_exchange.publish(message, routing_key="")

        print(f" [x] Sent order paid event {payload}")
