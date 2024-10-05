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
  libatk1.0-0 \
  libcups2 \
  libdbus-glib-1-2 \
  libgtk-3-0 \
  libx11-dev \
  libgdk-pixbuf2.0-0 \
  libpango1.0-0 \
  libpangocairo-1.0-0 \
  libasound2 \
  fonts-liberation \
  libappindicator3-1 \
  libxshmfence1 \
  chromium \
  && rm -rf /var/lib/apt/lists/*

ENV CHROMEDRIVER_VERSION=129.0.6668.89


RUN wget -N https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
  unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
  chmod +x /usr/local/bin/chromedriver && \
  rm chromedriver_linux64.zip

ENV DISPLAY=:99

WORKDIR /usr/api

COPY ./requirements.txt /usr/api/requirements.txt

RUN pip install --upgrade pip 
RUN pip install -r /usr/api/requirements.txt 

COPY ./app /usr/api/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
