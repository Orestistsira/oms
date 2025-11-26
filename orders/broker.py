import json
import os
import asyncio
from aio_pika import Message, connect, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractIncomingMessage

from db_handler import DBHandler

RABBIT_URI = os.getenv("RABBIT_URI", "amqp://guest:guest@rabbitmq/")

class Broker:
    def __init__(self, db_handler: DBHandler):
        self.db_handler = db_handler
        asyncio.create_task(self.consume_order_paid())

    async def publish_order_created(self, order: dict):
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

    async def on_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process():
            data = json.loads(message.body.decode())
            print(f"[x] Received order.paid: {data}", flush=True)

            try:
                await self.db_handler.update_order(
                    data["order_id"],
                    {
                        "status": "paid",
                        "payment_link": ""
                    }
                )
            except Exception as e:
                print(f"Database error: {e}")

    async def consume_order_paid(self):
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
            await queue.consume(self.on_message)

            print(" [*] Waiting for order paid events", flush=True)
            await asyncio.Future()