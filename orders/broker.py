import json
from aio_pika import Message, connect, DeliveryMode

async def publish_order_created(order: dict):
    # Perform connection
    connection = await connect("amqp://guest:guest@rabbitmq/")

    async with connection:
        # Creating a channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue("hello")

        # Sending the message
        await channel.default_exchange.publish(
            Message(body=json.dumps(order, default=str).encode(), content_type="application/json", delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=queue.name,
        )

        print(f" [x] Sent Order: {order}")