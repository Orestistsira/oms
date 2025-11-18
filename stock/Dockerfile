FROM python:3.11-slim

RUN mkdir /service
COPY proto/ /service/proto/
COPY stock/ /service/stock/
WORKDIR /service/stock
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN python -m grpc_tools.protoc -I ../proto --python_out=. \
           --grpc_python_out=. ../proto/orders.proto

CMD ["python", "-u", "main.py"]
