import json
import os
import asyncio
from aio_pika import Message, connect, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractIncomingMessage

from db_handler import DBHandler

RABBIT_URI = os.getenv("RABBIT_URI", "amqp://guest:guest@rabbitmq/")

async def publish_order_created(order: dict):
    # Perform connection
    connection = await connect(RABBIT_URI)

    async with connection:
        # Creating a channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue("order.created")

        # Sending the message
        await channel.default_exchange.publish(
            Message(body=json.dumps(order, default=str).encode(), content_type="application/json", delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=queue.name,
        )

        print(f" [x] Sent Order: {order}")

async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        data = json.loads(message.body.decode())
        print(f"[x] Received order.paid: {data}", flush=True)

        db_handler = DBHandler()
        try:
            await db_handler.update_order(
                data["order_id"],
                {
                    "status": "paid",
                    "payment_link": ""
                }
            )
        except Exception as e:
            print(f"Database error: {e}")

async def consume_order_paid():
    # Perform connection
    connection = await connect(RABBIT_URI)

    async with connection:
        # Creating a channel
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        order_paid_exchange = await channel.declare_exchange(
            "order.paid", ExchangeType.FANOUT,
        )

        # Declaring queue
        queue = await channel.declare_queue(exclusive=True)

        # Binding the queue to the exchange
        await queue.bind(order_paid_exchange)

        # Start listening the queue
        await queue.consume(on_message)

        print(" [*] Waiting for order paid events", flush=True)
        await asyncio.Future()