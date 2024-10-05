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

RUN apt-get install -y google-chrome-stable
RUN wget -N https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
  unzip -o chromedriver-linux64.zip -d /usr/local/bin/ && \
  mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
  chmod +x /usr/local/bin/chromedriver && \
  rm -rf chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64


WORKDIR /usr/api

COPY ./requirements.txt /usr/api/requirements.txt

RUN pip install --upgrade pip 
RUN pip install -r /usr/api/requirements.txt 

COPY ./app /usr/api/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
