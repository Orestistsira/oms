# stock/main.py
import asyncio
import grpc

from db_handler import DBHandler
import orders_pb2, orders_pb2_grpc

class StockServicer(orders_pb2_grpc.StockServicer):
    def __init__(self):
        self.db_handler = DBHandler()

    async def CheckIfItemsInStock(self, request, context):
        req_items = self._merge_items(request.items)
        item_ids = req_items.keys()

        print(item_ids)
        try:
            stock_items = await self.db_handler.get_items(
                item_ids=list(item_ids)
            )
        except Exception as e:
            print(f"Database error: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to get stock items: {str(e)}"
            )
        print(stock_items)

        items = []
        for stock_item in stock_items:
            item_id = stock_item["_id"]
            available_quantity = stock_item["quantity"]
            requested_quantity = req_items.get(item_id, 0)

            if available_quantity < requested_quantity:
                return orders_pb2.CheckIfItemsInStockResponse(
                    in_stock=False,
                    items=[
                        orders_pb2.Item(
                            item_id=item_id,
                            name=stock_item["name"],
                            price=stock_item["price"],
                            quantity=available_quantity
                        ) for stock_item in stock_items
                    ]
                )

            items.append(orders_pb2.Item(
                item_id=item_id,
                name=stock_item["name"],
                price=stock_item["price"]*requested_quantity,
                quantity=requested_quantity
            ))

        # TODO: Deduct/Reserve stock quantities here or in a separate method

        return orders_pb2.CheckIfItemsInStockResponse(
            in_stock=True,
            items=items
        )

    async def GetItems(self, request, context):
        pass

    def _merge_items(self, items):
        merged_items = {}
        for item in items:
            if item.item_id in merged_items:
                merged_items[item.item_id] += item.quantity
            else:
                merged_items[item.item_id] = item.quantity
        return merged_items
        

async def serve():
    server = grpc.aio.server()
    orders_pb2_grpc.add_StockServicer_to_server(StockServicer(), server)
    listen_addr = "[::]:2001"
    server.add_insecure_port(listen_addr)
    print(f"gRPC server starting on {listen_addr}")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
