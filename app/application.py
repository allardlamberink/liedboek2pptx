''' pptx-generator
    initial development start date: 2016-06-26
    initial release date: 2017-04-09
    copyright (c) 2016-2023 by A.D. Lamberink        
'''

from datetime import date, datetime, timedelta
from flask import Flask, request, redirect, url_for, flash, render_template, make_response, jsonify, send_file
from threading import Thread
from uuid import uuid4
from werkzeug.utils import secure_filename
import ast
import createpptx
import os
import sys


application = Flask(__name__)
create_pptx_processes = {}
sw_ver = '0.3'

###################  command_line part ####################
def start_cmdline():
    # TODO: read these parameters from the command-line or change this cmdline part of the app to a py.TEST
    voorganger = 'Ds. naam'
    organist = 'Organist naam'
    datum_tekst = 'vrijdag 14 april 2018'
    #scripture_fragments = ['Johannes 19: 23-30','Mattheüs 3: 15-20']
    scripture_fragments = [b'Johannes 19: 23-30',] # flash is sending in binary format, so keep this for the test
    titel_tekst = 'Welkom!'
    sub_titel_tekst = datum_tekst + u'\nVoorganger: ' + voorganger + u'\nOrganist: ' + organist
    uploaded_zipfilename = 'liedboek.zip'
    upload_path = application.config['UPLOAD_FOLDER']
    cpp = createpptx.CreatePPTXProcess(file_uuid='cmdlineversion')
    liedvolgorde = ['23b','802']
    cpp.setparams(upload_path, uploaded_zipfilename, liedvolgorde, voorganger, organist, datum_tekst, scripture_fragments, titel_tekst, sub_titel_tekst)
    cpp.start()
    return


###################  web part ####################
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['zip'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

application.secret_key = 'some_secret'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # max 16 MB


#@app.route('/')
#def hello_world():
#   return 'Hello, World!'

#@app.route('/favicon.ico')
#def favicon():
#    """Renders the favicon."""
#return send_from_directory(path.join(app.root_path, 'static'),
#                           'favicon.ico')


@application.route('/downloadresult', methods=['GET'])
def downloadresult():
    try:
        file_uuid = secure_filename(request.args.get('file_uuid', ''))
        if file_uuid:
            filename = '%s.pptx' % file_uuid
        return send_file(path_or_file=os.path.join(application.config['UPLOAD_FOLDER'], filename), download_name='hervgemb_presentatie_%s.pptx' % datetime.now().strftime('%Y%m%d%H%M'), as_attachment=True)
    except Exception as e:
        return str(e)

@application.route('/sortliturgie', methods=['GET'])
def sortliturgie():
    uploaded_zipfilename = request.args.get('uploaded_zipfilename', None)
    if not uploaded_zipfilename:
        flash('geen file geupload')
        return redirect(url_for('upload_file'))
    else:
        uploaded_zipfilename_secure = secure_filename(uploaded_zipfilename)  # secure again
        uploaded_zipfilename_secure = os.path.join(application.config['UPLOAD_FOLDER'], uploaded_zipfilename_secure)
        cpp = createpptx.CreatePPTXProcess()
        zip_obj = cpp.get_zip_obj(uploaded_zipfilename_secure)
        filenamelist = cpp.get_filenamelist(zip_obj)
        zip_obj.close()
        song_couplets = cpp.song_couplets2arr(filenamelist)
        liturgielijst = []
        maanden = ['dummy', 'januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']
        next_sunday_dt = date.today() + timedelta( (6-date.today().weekday()) % 7 )
        next_sunday_formatted = next_sunday_dt.strftime(f"zondag {next_sunday_dt.day} {maanden[next_sunday_dt.month]} %Y")

        for song, couplets in song_couplets.items():
            #for couplet in couplets:  # TODO: per couplet sorteren mogelijk maken...
            coupletstr = ', '.join(couplets)
            liturgielijst.append([song, coupletstr])  #'{0}: {1}'.format(song, coupletstr))
        return render_template('sortliturgie.html', name='sortliturgie',liturgielijst=liturgielijst, uploaded_zipfilename=uploaded_zipfilename_secure, next_sunday_date=next_sunday_formatted)


#@app.route('/login', methods=['GET', 'POST'])
#def login():
#    error = None
#    if request.method == 'POST':
#        if request.form['username'] != 'admin' or \
#            request.form['password'] != 'secret':
#            error = 'Invalid credentials'
#        else:
#            flash('You were successfully logged in')
#            return redirect(url_for('sortliturgie'))
#    return render_template('login.html', error=error)



#@app.route('/upload', methods=['GET', 'POST'])
@application.route('/', methods=['GET', 'POST'])
def upload_file():
    error=None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
                #flash('upload=suc6')
                return redirect(url_for('sortliturgie', uploaded_zipfilename=filename))
            else:
                flash('Invalid filetype (only .zip is allowed)')

    return render_template('upload.html', introtekst='Upload liedboek.nu zip-bestand', sw_ver=sw_ver, errormsg=error)



@application.route('/summary', methods=['POST'])
def summary():
    if request.method == 'POST':
        finalliturgielijst = []
        scripture_fragments = []
        # check if the post request has the file part
        if 'liedvolgorde' not in request.form:
            flash('Geen liederen gevonden')
        else:
            liedlist = request.form['liedvolgorde'].split(',')
            liturgietypestr = request.form['liturgietype']
            #flash('Wel liederen gevonden {0}. Liturgietype={1}'.format(liedlist,liturgietypestr))

        for lied in liedlist:
            finalliturgielijst.append(lied)
        
        uploaded_zipfilename = request.form['uploaded_zipfilename']
        voorganger = request.form['voorganger']
        organist = request.form['organist']
        datum_tekst = request.form['datum']
        titel_tekst = request.form['titeltekst']
        sub_titel_tekst = datum_tekst + '\nVoorganger: ' + voorganger + '\nOrganist: ' + organist
        if request.form['scripture_fragment_1']:
            scripture_fragments.append(request.form['scripture_fragment_1'].encode('utf-8'))
        if request.form['scripture_fragment_2']:
            scripture_fragments.append(request.form['scripture_fragment_2'].encode('utf-8'))

        return render_template('summary.html', uploaded_zipfilename=uploaded_zipfilename, liturgietype=liturgietypestr, 
                                finalliturgielijst=finalliturgielijst, 
                                voorganger=voorganger, organist=organist, datum_tekst=datum_tekst, scripture_fragments=scripture_fragments,
                                titel_tekst=titel_tekst, sub_titel_tekst=sub_titel_tekst) 


@application.route('/process/start/<process_class_name>/')
def process_start(process_class_name):
    process_module_name = process_class_name
    #if process_class_name != 'CreatePPTXProcess':
    process_module_name = process_module_name.replace('Process', '')
    process_module_name = process_module_name.lower()
    # Dynamically import the class / module for the particular process
    # being started. This saves needing to import all possible
    # modules / classes.
    # TODO subdirectories maken:process_module_obj = __import__('%s.%s.%s' % ('test_progress_thread',
    #                                              'CreatePPTXProcess',
    #                                              process_module_name),
    #                                              fromlist=[process_class_name])

    process_module_obj = __import__('%s' % (process_module_name),
                                            fromlist=[process_class_name])

    process_class_obj = getattr(process_module_obj, process_class_name)
    key = str(uuid4())
    
    args = []
    extra_args_input = request.args.get('extra_args', '', type=str)
    if extra_args_input != '':
        args = extra_args_input.split(';')
    kwargs = {
        'file_uuid': key,
    }
    
    # Initialise the process thread object.
    cpx = process_class_obj(*args, **kwargs)

    uploaded_zipfilename = request.args.get('uploaded_zipfilename')
    voorganger = request.args.get('voorganger')
    organist = request.args.get('organist')
    datum_tekst = request.args.get('datum_tekst')
    scripture_fragments = ast.literal_eval(request.args.get('scripture_fragments'))
    titel_tekst = request.args.get('titel_tekst')
    sub_titel_tekst = request.args.get('sub_titel_tekst')
    liedvolgorde = ast.literal_eval(request.args.get('finalvolgorde'))
    
    cpx.setparams(application.config['UPLOAD_FOLDER'], uploaded_zipfilename, liedvolgorde, voorganger, organist, datum_tekst, scripture_fragments, titel_tekst, sub_titel_tekst)
    cpx.start()
    
    if not process_class_name in create_pptx_processes:
        create_pptx_processes[process_class_name] = {}
    
    # Store the process thread object in a global dict variable, so it
    # continues to run and can have its progress queried, independent
    # of the current session or the current request.
    create_pptx_processes[process_class_name][key] = cpx
    
    percent_done = round(cpx.percent_done(), 1)
    done=False
    
    return jsonify(key=key, percent=percent_done, done=done)


@application.route('/process/progress/<process_class_name>/')
def process_progress(process_class_name):
    key = request.args.get('key', '', type=str)
    
    if not process_class_name in create_pptx_processes:
        create_pptx_processes[process_class_name] = {}
    #print("debug key = {0}".format(key))
    #print("debug process_class_name = {0}".format(process_class_name))
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




############################ entry point (main) ####################
if __name__ == "__main__":
    print(f"PowerPoint generator {sw_ver}")
    start_cmdline()
    # the local / web/flask version is started by uwsgi --ini ./uwsgi_debug.ini
    '''arv = sys.argv[1:]
    if(len(arv)>0):
        if arv[0] == '-c':  # start command-line version
        else:
            print("invalid argument")
    else:
        start_web()
    '''
