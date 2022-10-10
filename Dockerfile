FROM python:3-slim

ENV PYTHONUNBUFFERED=1
ARG APP_ENV="production"
ENV APP_ENV $APP_ENV

# Alternatives for APP_ENV:
# - production: for production deployment
# - development: for local development environment
# - ci: for continous integration environment


COPY requirements.txt dev_requirements.txt /

RUN apt-get update && \
    apt-get install -y build-essential git libpq-dev && \
    pip install -r /requirements.txt && \
    if [ "$APP_ENV" = "production" ]; then apt-get clean ; fi

RUN if [ "$APP_ENV" != "production" ]; then pip install -r /dev_requirements.txt ; fi

ADD django /usr/local/app

WORKDIR /usr/local/app

EXPOSE 8000

CMD ["/usr/local/bin/gunicorn", "--config", "/usr/local/app/gunicorn.py", "-b", ":8000", "celsure.wsgi:application"]
