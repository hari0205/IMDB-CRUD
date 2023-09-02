# Use an official Python runtime as a parent image
FROM python:3.9.6-slim-buster


WORKDIR /app


COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

#DB migrations
RUN flask db init
RUN flask db migrate
RUN flask db upgrade

ENV FLASK_APP=app

EXPOSE 5000

