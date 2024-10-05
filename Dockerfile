FROM python:3.12 AS base

RUN apt-get update && apt-get install -y \
  libglib2.0-0 \
  libnss3 \
  libgconf-2-4 \
  libfontconfig1 \
  chromium-driver \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


ENV CHROMEDRIVER_VERSION=129.0.6668.89

RUN wget -N https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
  unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
  chmod +x /usr/local/bin/chromedriver && \
  rm chromedriver_linux64.zip

WORKDIR /usr/api

COPY ./requirements.txt /usr/api/requirements.txt

RUN pip install --upgrade pip 
RUN pip install -r /usr/api/requirements.txt 

COPY ./app /usr/api/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
