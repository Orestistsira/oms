from contextlib import asynccontextmanager
from fastapi import FastAPI
from broker import consume_order_created
import asyncio
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start consumer
    asyncio.create_task(consume_order_created())
    yield

app = FastAPI(title="Payment Service", lifespan=lifespan)

@app.post("/payment/callback")
async def payment_callback(order_id: str):
    # await app.state.payment_service.handle_payment_completed(order_id)
    return {"status": "ok"}
