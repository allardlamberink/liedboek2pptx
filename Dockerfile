FROM debian:stretch
LABEL maintainer="Allard Lamberink <allard@lamberink.com>"
RUN apt-get update
RUN apt-get install -y python python-dev python-pip nginx libjpeg-dev libpng-dev vim
RUN pip install uwsgi
COPY ./ ./app
WORKDIR ./app
RUN pip install -r requirements.txt
COPY ./nginx.conf /etc/nginx/sites-available/default
CMD service nginx start && uwsgi -s /tmp/uwsgi.sock --processes=5 --chmod-socket=666 --manage-script-name --mount /=application:application
