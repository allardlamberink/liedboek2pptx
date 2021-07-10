''' "pptx-generator v0.1"        
     initial development start date: 2016-06-26        
     initial release date: 2017-04-09
     copyright (c) 2016-2017 by A.D. Lamberink        
'''

# todo: toevoegen uitzondering voor lied 802, hierin wordt het refrein niet correct meegenomen
# 2017-01-21: mail uit naar liedboek.nu met verzoek om verbetering

import sys
from flask import Flask, request, redirect, url_for, flash, render_template, make_response, jsonify, send_file
from werkzeug.utils import secure_filename
from uuid import uuid4
from datetime import date, timedelta
import os
from createpptx import CreatePPTXProcess
import ast

application = Flask(__name__)
create_pptx_processes = {}


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
        import pdb
        pdb.set_trace()
        print("inside downloadresult")
        file_uuid = secure_filename(request.args.get('file_uuid', ''))
        if file_uuid:
            filename = '%s.pptx' % file_uuid
        return send_file(os.path.join(application.config['UPLOAD_FOLDER'], filename), attachment_filename='hervgemb_presentatie_%s.pptx' % file_uuid, as_attachment=True)
    except Exception as e:
        return str(e)

@application.route('/sortliturgie', methods=['GET'])
def sortliturgie():
    print("inside sortliturgie")
    uploaded_zipfilename = request.args.get('uploaded_zipfilename', None)
    if not uploaded_zipfilename:
        flash('geen file geupload')
        return redirect(url_for('upload_file'))
    else:
        uploaded_zipfilename_secure = secure_filename(uploaded_zipfilename)  # secure again
        uploaded_zipfilename_secure = os.path.join(application.config['UPLOAD_FOLDER'], uploaded_zipfilename_secure)
        cpp = CreatePPTXProcess()
        zip_obj = cpp.get_zip_obj(uploaded_zipfilename_secure)
        filenamelist = cpp.get_filenamelist(zip_obj)
        zip_obj.close()
        song_couplets = cpp.song_couplets2arr(filenamelist)
        liturgielijst = []
        maanden = ['dummy', 'januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']
        next_sunday_date = (date.today() + timedelta( (6-date.today().weekday()) % 7 )).strftime("zondag %d {0} %Y".format(maanden[date.today().month]))
        for song, couplets in song_couplets.iteritems():
            #for couplet in couplets:  # todo: per couplet sorteren mogelijk maken...
            coupletstr = ', '.join(couplets)
            liturgielijst.append([song, coupletstr])  #'{0}: {1}'.format(song, coupletstr))
        #liturgielijst = song_couplets   #{ 'title': 'allard', 'Age': 7 }
        return render_template('sortliturgie.html', urlforsummary=url_for('summary'), name='test van Allard', liturgielijst=liturgielijst, uploaded_zipfilename=uploaded_zipfilename_secure, next_sunday_date=next_sunday_date)


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
    print("inside upload_file")
    try:
        error=None
        if request.method == 'POST':
            print("inside upload_file method post")
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(url_for(request.url))
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(url_for(request.url))
            if file:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
                    #flash('upload=suc6')
                    return redirect(url_for('sortliturgie', uploaded_zipfilename=filename))
                else:
                    flash('Invalid filetype (only .zip is allowed)')
    except Exception as ex:
        print("fout bij upload {0} - {1}".format(ex.args, ex.message))
    return render_template('upload.html', urlforupload=url_for('upload_file'), introtekst='Upload liedboek.nu zip-bestand', errormsg=error)



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

        return render_template('summary.html', urlforcreatepptx=url_for('createpptx'), urlfordownloadresult=url_for('downloadresult'), uploaded_zipfilename=uploaded_zipfilename, liturgietype=liturgietypestr, finalliturgielijst=finalliturgielijst, voorganger=voorganger, organist=organist, datum_tekst=datum_tekst, scripture_fragments=scripture_fragments, titel_tekst=titel_tekst, sub_titel_tekst=sub_titel_tekst)




@application.route('/createpptx', methods=['POST'])
def createpptx():
    retval = False
    print("inside createpptx")
    #uploaded_zipfilename = request.args.get('uploaded_zipfilename', None)
    #if not uploaded_zipfilename:
    #    flash('geen file geupload')
    #    return redirect(url_for('upload_file'))
#    key = str(uuid4())
    cpp = CreatePPTXProcess()
    uploaded_zipfilename = request.values.get('uploaded_zipfilename')
    voorganger = request.values.get('voorganger')
    organist = request.values.get('organist')
    datum_tekst = request.values.get('datum_tekst')
    scripture_fragments = ast.literal_eval(request.values.get('scripture_fragments'))
    titel_tekst = request.values.get('titel_tekst')
    sub_titel_tekst = request.values.get('sub_titel_tekst')
    volgordelist = ast.literal_eval(request.values.get('liedvolgorde'))
    
    cpp.setparams(application.config['UPLOAD_FOLDER'], uploaded_zipfilename, volgordelist, voorganger, organist, datum_tekst, scripture_fragments, titel_tekst, sub_titel_tekst)
    
    retval = cpp.run()
#    percent_done = round(cpx.percent_done(), 1)
    percent_done = 5.0
    done=True
#    
    import pdb
    pdb.set_trace()
    print("allard check retval")
    return jsonify(retval=retval, percent=percent_done, done=done)

@application.route('/getprogress', methods=['GET'])
def getprogress():
    key = request.args.get('key', '', type=str)
    
    percent_done = 5.0
    percent_done = round(percent_done, 1)
    
    return jsonify(key=key, percent=percent_done, done=done)

