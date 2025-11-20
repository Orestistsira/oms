FROM python:3.11-slim

RUN mkdir /service
COPY proto/ /service/proto/
COPY payment/ /service/payment/
WORKDIR /service/payment
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN python -m grpc_tools.protoc -I ../proto --python_out=. \
           --grpc_python_out=. ../proto/orders.proto

CMD ["fastapi", "run", "main.py", "--port", "8001"]
