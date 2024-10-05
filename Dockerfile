FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y \
  curl \
  unzip \
  wget \
  gnupg2 \
  libnss3 \
  libgconf-2-4 \
  libxss1 \
  libxi6 \
  libxrender-dev \
  libfontconfig1 \
  libx11-xcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxtst6 \
  libxrandr2 \
  chromium \
  && rm -rf /var/lib/apt/lists/*

RUN CHROMEDRIVER_VERSION=curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE && \
  wget -N https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
  unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
  chmod +x /usr/local/bin/chromedriver && \
  rm chromedriver_linux64.zip


WORKDIR /usr/api

COPY ./requirements.txt /usr/api/requirements.txt

RUN pip install --upgrade pip 
RUN pip install -r /usr/api/requirements.txt 

COPY ./app /usr/api/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]