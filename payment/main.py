from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from broker import consume_order_created, publish_order_paid
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start consumer
    asyncio.create_task(consume_order_created())
    yield

app = FastAPI(title="Payment Service", lifespan=lifespan)

@app.post("/payment/{order_id}/callback", response_model=dict, status_code=status.HTTP_200_OK)
async def payment_callback(order_id: str):
    try:
        await publish_order_paid(order_id)
    except Exception as e:
        return {"detail": f"error: {e}"}
    return {"detail": "payment processed"}
