FROM python:3.12-slim AS base

RUN apt-get install -y libglib2.0 libnss3 libgconf-2-4 libfontconfig1 chromium-driver

WORKDIR /usr/api

COPY ./requirements.txt /usr/api/requirements.txt

RUN pip install --upgrade pip 
RUN pip install -r /usr/api/requirements.txt 

COPY ./app /usr/api/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
