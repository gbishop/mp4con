from app import app
from flask import render_template, request, Response, url_for, jsonify
import converter as con
import time
import tempfile
import datetime
import os
import re
import shutil
from multiprocessing import Process
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

ALLOWED_EXTENSIONS = set(['mp4', 'mov', 'png'])
ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = ROOT + "/static/"
TEMP = STATIC + "temp/"

#### ROUTES ####


@app.route('/')
@app.route('/index')
def index():
    cleanup()
    return render_template('index.html')


@app.route('/_upload', methods=['POST'])
def upload():
    """Handles file uploading.

    Returns:
        Nothing if the file upload failed; path to the temporary folder if it succeedes
    """
    if not (validate(request.files)):
        return ""
    dfile = request.files['video']
    filename = dfile.filename
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    target = tempfile.mkdtemp(dir=TEMP, prefix=date)
    destination = "/".join([target, filename])
    dfile.save(destination)
    abs_path = con.split(target, filename, amnt=50, delta=50)
    rel_path = "/".join(abs_path.split("/")[-3:])
    return rel_path


@app.route('/_get_frames', methods=['GET'])
def getFrames():
    "Gives sorted order of frames in a folder"
    print(request.args.get('folder'))
    ret = ([int(f[:-4])
            for f in os.listdir(STATIC + request.args.get('folder')) if f.endswith('.png')])
    return jsonify(sorted(ret, key=int))


@app.route('/_split_end', methods=['POST'])
def split_end():
    print(request.get_json())
    json = request.get_json()
    ret = con.split(TEMP + json['folder'], json['name'],
                    amnt=50, delta=50, direction='backward')
    return "/".join(ret.split("/")[-3:])


@app.route('/_split_mid', methods=['POST'])
def split_mid():
    json = request.get_json()
    ret = con.split(TEMP + json['folder'], json['name'],
                    init=int(json['init']) - 50, amnt=20, delta=5)
    return "/".join(ret.split("/")[-3:])


@app.route('/_predict', methods=['GET'])
def predict():
    tdims, pdims = con.estimate(STATIC + request.args.get('folder') +
                                '/' + request.args.get('frame') + '.png')
    return jsonify({"tdims": tdims, "pdims": pdims})


@app.route('/_to_csv', methods=['POST'])
def to_csv():
    json = request.get_json()
    print(json)
    pdims = json['picdims']
    picdims = [pdims['x'], pdims['y'], pdims['x'] +
               pdims['width'], pdims['y'] + pdims['height']]
    tdims = json['textdims']
    textdims = [tdims['x'], tdims['y'], tdims['x'] +
                tdims['width'], tdims['y'] + tdims['height']]
    # send_csv(con, TEMP + json['folder'], json['name'],
            #  picdims, textdims, json['init'], json['end'])
    p = Process(target=send_csv, args=(con, TEMP + json['folder'], json['name'],
       picdims, textdims, json['init'], json['end'], json['email']))
# 
    p.start()
    return ""

#### METHODS ####


def send_csv(con, path, name, pdims, tdims, init, end, email):
    data = con.convert(os.path.join(path, name), pdims, tdims, init, end)
    with open (data, 'r') as file:
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


def validate(dfile):
    filename = dfile['video'].filename
    if filename == '':
        return False
    return allowed_file(filename) and dfile


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup():
    if not os.path.isdir(os.path.join(STATIC, "temp/")):
        os.mkdir(os.path.join(STATIC, "temp/"))
    key = r'(\d+-)+\d+'
    now = datetime.datetime.now()
    for folder in os.listdir('app' + url_for('static', filename='temp')):
        match = re.search(key, folder[:10])
        if match:
            td = now - datetime.datetime.strptime(match.group(0), '%Y-%m-%d')
            if td.days > 0:
                shutil.rmtree('app' + url_for('static',
                                              filename='temp') + '/' + folder)

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
