FROM python:3.11

RUN mkdir /backend

WORKDIR /backend

ADD . .

RUN pip install -r req.txt

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]