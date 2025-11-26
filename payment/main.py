from contextlib import asynccontextmanager
from fastapi import FastAPI
from broker import consume_order_created, publish_order_paid
import asyncio
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start consumer
    asyncio.create_task(consume_order_created())
    yield

app = FastAPI(title="Payment Service", lifespan=lifespan)

@app.post("/payment/{order_id}/callback")
async def payment_callback(order_id: str):
    await publish_order_paid(order_id)
    return {"status": "ok"}
