# Generate gRPC code from .proto files
python -m grpc_tools.protoc -I proto --python_out=proto --grpc_python_out=proto proto/orders.proto

cp ./proto/orders_pb2.py ./orders/
cp ./proto/orders_pb2_grpc.py ./orders/

cp ./proto/orders_pb2.py ./gateway/
cp ./proto/orders_pb2_grpc.py ./gateway/

cp ./proto/orders_pb2.py ./stock/
cp ./proto/orders_pb2_grpc.py ./stock/

cp ./proto/orders_pb2.py ./payment/
cp ./proto/orders_pb2_grpc.py ./payment/