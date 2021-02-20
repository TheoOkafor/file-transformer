FROM python:3.9.1-buster

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY ./src /src

COPY .env .env

CMD python3.9 src/app.py

EXPOSE 8000
