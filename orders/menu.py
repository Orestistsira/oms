menu = {
    "item1": {"name": "Burger", "price": 15},
    "item2": {"name": "Fanta", "price": 7},
    "item3": {"name": "Fries", "price": 10},
}

def get_items_with_details(items):
    detailed_items = []
    for item in items:
        item_id = item.item_id
        menu_item = menu.get(item_id)
        if menu_item is None:
            raise Exception(f"Item ID {item_id} not found in menu")

        detail = menu[item_id].copy()
        detail["item_id"] = item_id
        detail["name"] = menu[item_id]["name"]
        detail["quantity"] = item.quantity
        detail["price"] = menu[item_id]["price"] * item.quantity
        detailed_items.append(detail)
    return detailed_items