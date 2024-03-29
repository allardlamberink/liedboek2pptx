FROM tiangolo/uwsgi-nginx-flask:python3.10

COPY ./app/setup/requirements.txt /app/setup/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/setup/requirements.txt

ENV UWSGI_CHEAPER 0
ENV UWSGI_PROCESSES 1

COPY ./app /app
RUN chmod -R 755 /app/static/
