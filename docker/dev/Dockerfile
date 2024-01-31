# FROM 767397730645.dkr.ecr.ap-south-1.amazonaws.com/ecom-base:latest
FROM <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/ecom-base:latest
# FROM ecom-base:latest
#from python:3.8

ENV PATH="/appenv/bin:$PATH"

WORKDIR /application
# WORKDIR /
COPY src /application/src
# COPY src /src
COPY docker/dev/requirements.txt requirements.txt

COPY config /application/config
# COPY config /config

EXPOSE 8005

RUN pip install -r requirements.txt --use-pep517

CMD ["uwsgi", "config/uwsgi.ini"]
