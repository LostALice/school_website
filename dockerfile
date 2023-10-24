FROM python:3.11

RUN mkdir /backend

WORKDIR /backend

ADD . .

RUN pip install -r req.txt

WORKDIR /backend/backend

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "main:app", "--port", "8080"]
