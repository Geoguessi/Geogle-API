FROM python:3.12-slim AS base

WORKDIR /usr/api

COPY ./requirements.txt /usr/api/requirements.txt

RUN pip install --upgrade pip 
RUN pip install -r /usr/api/requirements.txt 

COPY ./app /usr/api/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
