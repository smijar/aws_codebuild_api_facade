# pull official base image
FROM python:3.9.0-slim-buster

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get -y install netcat gcc curl httpie \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .

CMD ["uvicorn", "app.main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]
