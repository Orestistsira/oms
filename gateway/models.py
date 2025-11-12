from pydantic import BaseModel


class ItemWithQuantity(BaseModel):
    item_id: str
    quantity: int


class CreateOrderRequest(BaseModel):
    items: list[ItemWithQuantity]