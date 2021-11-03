FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app/setup/requirements.txt /app/setup/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/setup/requirements.txt

COPY ./app /app
