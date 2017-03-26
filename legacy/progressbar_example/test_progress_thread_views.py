from glob import glob
from operator import itemgetter
from os import path
import sys
import time
from uuid import uuid4

from flask import current_app as app
from flask import jsonify
from flask import Flask
from flask import render_template
from flask import request
from flask import Response
from flask import send_from_directory
from werkzeug.exceptions import NotFound

app = Flask(__name__)
create_pptx_processes = {}

@app.route('/')
def home():
    return render_template('test_home.html', arg1="home")


@app.route('/process/start/<process_class_name>/')
def process_start(process_class_name):
    #arg1 = request.args.get('filenames_input', '', type=str)
    process_module_name = process_class_name
    #if process_class_name != 'CreatePPTXProcess':
    process_module_name = process_module_name.replace('Process', '')
    process_module_name = process_module_name.lower()
    # Dynamically import the class / module for the particular process
    # being started. This saves needing to import all possible
    # modules / classes.
    # todo allard subdirectories maken:process_module_obj = __import__('%s.%s.%s' % ('test_progress_thread',
    #                                              'CreatePPTXProcess',
    #                                              process_module_name),
    #                                              fromlist=[process_class_name])

    process_module_obj = __import__('%s' % (process_module_name),
                                            fromlist=[process_class_name])

    process_class_obj = getattr(process_module_obj, process_class_name)
    
    args = []
    #arg2 = request.args.get('filebrowse_path', '', type=str)
    extra_args_input = request.args.get('extra_args', '', type=str)
    if extra_args_input != '':
        args = extra_args_input.split(';')
    kwargs = {
        'allard_str': 'allard_str_tst',
    }
    
    # Initialise the process thread object.
    cpx = process_class_obj(*args, **kwargs)
    cpx.start()
    
    if not process_class_name in create_pptx_processes:
        create_pptx_processes[process_class_name] = {}
    key = str(uuid4())
    
    # Store the process thread object in a global dict variable, so it
    # continues to run and can have its progress queried, independent
    # of the current session or the current request.
    create_pptx_processes[process_class_name][key] = cpx
    
    percent_done = round(cpx.percent_done(), 1)
    done=False
    
    return jsonify(key=key, percent=percent_done, done=done)


@app.route('/process/progress/<process_class_name>/')
def process_progress(process_class_name):
    key = request.args.get('key', '', type=str)
    
    if not process_class_name in create_pptx_processes:
        create_pptx_processes[process_class_name] = {}
    
    if not key in create_pptx_processes[process_class_name]:
        return jsonify(error='Invalid process key.')
    
    # Retrieve progress of requested process thread, from global
    # dict variable where the thread reference is stored.
    percent_done = create_pptx_processes[process_class_name][key] \
                   .percent_done()
    
    done = False
    if not create_pptx_processes[process_class_name][key].is_alive() or \
       percent_done == 100.0:
        del create_pptx_processes[process_class_name][key]
        done = True
    percent_done = round(percent_done, 1)
    
    return jsonify(key=key, percent=percent_done, done=done)


#@app.route('/favicon.ico')
#def favicon():
#    """Renders the favicon."""
#return send_from_directory(path.join(app.root_path, 'static'),
#                           'favicon.ico')
