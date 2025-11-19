from datetime import datetime
from pydantic import BaseModel

class ItemWithQuantity(BaseModel):
    item_id: str
    quantity: int

class CreateOrderRequest(BaseModel):
    items: list[ItemWithQuantity]

class Order(BaseModel):
    order_id: str
    customer_id: str
    items: list[ItemWithQuantity]
    status: str
    payment_link: str | None = None
    created_at: datetime