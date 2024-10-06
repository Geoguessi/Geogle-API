FROM ubuntu:22.04

FROM python:3.8

RUN apt-get update

RUN apt install unzip

COPY chrome_114_amd64.deb ./

RUN apt install ./chrome_114_amd64.deb -y

RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip

RUN unzip chromedriver_linux64.zip

RUN mv chromedriver /usr/bin/chromedriver

RUN google-chrome --version

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
