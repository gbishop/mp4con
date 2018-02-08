from flask import render_template, request, redirect, url_for, jsonify, send_file
import os
import converter as con
from app import app
import cv2
import test
import threading
from multiprocessing import Process
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tempfile
import datetime
import shutil
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = ROOT + "/static/"
TEMP = STATIC + "temp/"

ALLOWED_EXTENSIONS = set(['mp4', 'mov'])


# TODO
# Look into python virtual environments
# python way of handling temp files.
# Look into python processing rather than threading (LATER, NOT NOW)
##


def validate(files):
    if 'file' not in files:
        print('No file found!')
        return redirect(request.url)
    ufile = files['file']
    filename = ufile.filename
    if filename == '':
        print('No selected file')
        return redirect(request.url)
    return allowed_file(filename) and ufile


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup():
    if not os.path.isdir(os.path.join(STATIC, "temp/")):
        os.mkdir(os.path.join(STATIC, "temp/"))
    key = r'(\d+-)+\d+'
    now = datetime.datetime.now()
    for folder in os.listdir('app'+url_for('static', filename='temp')):
        match = re.search(key, folder[:10])
        if match:
            td = now - datetime.datetime.strptime(match.group(0), '%Y-%m-%d')
            if td.days > 0:
                shutil.rmtree('app'+url_for('static', filename='temp')+'/'+folder)



@app.route('/test', methods=['POST', 'GET'])
def tt():
    return render_template('test.html')


@app.route('/_split_end', methods=['GET'])
def split_end():
    ret = con.split(request.args.get('root'), request.args.get('file'),
                    amnt=50, delta=50, direction='backward')
    return url_for('static', filename="/".join(ret.split("/")[-3:]))


@app.route('/_split_mid', methods=['GET'])
def split_mid():
    ret = con.split(request.args.get('root'), request.args.get('file'),
                    init=int(request.args.get('init'))-50, amnt=20, delta=5)
    return url_for('static', filename="/".join(ret.split("/")[-3:]))


@app.route("/", methods=['POST', 'GET'])
def index():
    """If GET, shows upload page, if POST, handles file upload and initial split
        before redirecting to frame selection."""
    print(os.listdir())
    cleanup()
    print("At index")
    if not request.method == 'POST':
        return render_template("upload.html")
    else:
        # If ppl upload bad stuff
        if not (validate(request.files)):
            print("invalid file")
            return redirect(request.url)
        print('You got past all the checks!')
        ufile = request.files['file']
        filename = ufile.filename
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        target = tempfile.mkdtemp(dir=TEMP, prefix=date)
        destination = "/".join([target, filename])
        ufile.save(destination)
        abs_path = con.split(target, filename, amnt=50, delta=50)
        rel_path = "/".join(abs_path.split("/")[-3:])
        print('THIS IS THE FOLDER: ' + rel_path)
        print(target, rel_path, filename)
    return render_template('select.html', folder=target, folder0=rel_path,
                           file=filename, rel_folder="/".join(target.split("/")[-2:]))


@app.route('/select_dims')
def select_dims():
    # con.split_1(STATIC+'/temp', request.args.get('name'),
    #            request.args.get('init_frame'))
    tdims, pdims = con.estimate(STATIC + '/temp/frames/0.png')
    return render_template('process.html',
                           img=request.args.get('folder'),
                           textdims=tdims,
                           picdims=pdims,
                           name=request.args.get('name'),
                           init=request.args.get('init_frame'),
                           end=request.args.get('end_frame'),
                           folder=".".join(request.args.get(
                               'folder').split("/")[-1:]),
                           parent=request.args.get('parent'))


def send_csv(con, path, name, pdims, tdims, init, end, email):
    data = con.convert(os.path.join(path,name), pdims, tdims, init, end)
    # Just a placeholder, will update to work properly on local machine when
    # hosted
    msg = MIMEMultipart()
    msg['Subject'] = 'converted csv'
    msg['From'] = 'gb.cs.unc.edu'
    body = 'DO NOT reply to this email, this account is only for sending out converted csv files'
    content = MIMEText(body, 'plain')
    msg.attach(content)
    attachment = MIMEText(data)
    attachment.add_header('Content-disposition', 'attachment',
                          filename="".join((name[:-3], 'csv')))
    msg.attach(attachment)
    s = smtplib.SMTP('fafnir.cs.unc.edu')
    s.sendmail('gb@cs.unc.edu', email, msg.as_string())
    s.quit()
    shutil.rmtree(path)
    print('done')


@app.route('/process', methods=['GET'])
def process():
    rarg = request.args.get
    def iarg(arg):
        return int(rarg(arg))
    tdims = [iarg('tcropx'), iarg('tcropy'), iarg('tcropx')+iarg('tcropw'),
             iarg('tcropy')+iarg('tcroph')]

    pdims = [iarg('pcropx'), iarg('pcropy'), iarg('pcropx')+iarg('pcropw'),
             iarg('pcropy')+iarg('pcroph')]

    p = Process(target=send_csv, args=(con, 'app/'+url_for('static', filename=rarg('parent')),
                                       rarg('name'), pdims, tdims,
                                       rarg('init'), rarg('end'),
                                       rarg('email')))
    p.start()

    return redirect(url_for('index'))


@app.route('/_return_frames', methods=['GET'])
def retFrames():
    ret = ([int(f[:-4])
            for f in os.listdir(ROOT+request.args.get('folder')) if f.endswith('.png')])
    return jsonify(sorted(ret, key=int))

   
        


# stops caching of images
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
