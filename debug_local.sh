#!/bin/bash
source ./liedboek2pptx_local.env
pyenv activate liedboek3pptx
cd app/
#uwsgi --ini ./uwsgi_debug.ini
python3 application.py
