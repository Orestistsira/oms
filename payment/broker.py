import asyncio
import json
from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage

async def on_message(message: AbstractIncomingMessage) -> None:
    """
    on_message doesn't necessarily have to be defined as async.
    Here it is to show that it's possible.
    """
    data = json.loads(message.body.decode())
    print(" [x] Received order.created:", data, flush=True)
    # print(f" [x] Received message {message.body}", flush=True)

async def consume_order_created():
    # Perform connection
    connection = await connect("amqp://guest:guest@rabbitmq/")
    async with connection:
        # Creating a channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue("hello")

        # Start listening the queue with name 'hello'
        await queue.consume(on_message, no_ack=True)

        print(" [*] Waiting for messages", flush=True)
        await asyncio.Future()
