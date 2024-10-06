FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

WORKDIR /app

RUN apt-get update && apt-get install -y \
  chromium-driver \
  chromium \
  curl \
  wget \
  xvfb \
  fonts-liberation \
  libappindicator3-1 \
  libnss3 \
  libxss1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]