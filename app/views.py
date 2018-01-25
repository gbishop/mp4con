from flask import render_template, request, redirect, url_for, jsonify, send_file
import sys
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

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = ROOT + "/static/"

ALLOWED_EXTENSIONS = set(['mp4', 'mov'])



# TODO
## Look into python virtual environments
## python way of handling temp files. 
## Look into python processing rather than threading (LATER, NOT NOW)
## 


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/test', methods=['POST', 'GET'])
def tt():

    return render_template('test.html')

@app.route('/_split_mid', methods=['POST', 'GET'])
def split_mid():
    con.mid_split(STATIC+'/temp', request.args.get('name'), request.args.get('frame'))
    return ''
@app.route('/_split_backward', methods=['POST', 'GET'])
def split_end():
    con.backward_split(STATIC+'/temp', request.args.get('name'))
    return ''

@app.route("/", methods=['POST', 'GET'])
def index():
    print(cv2.__version__)
    #print('ACTIVE THREADS', threading.active_count())
    if not request.method == 'POST':
        return render_template("upload.html")
    if not os.path.isdir(os.path.join(STATIC, "temp/")):
        os.mkdir(os.path.join(STATIC, "temp/"))
    print('You got to the upload method!')
    if request.method == 'POST':
        # If ppl upload bad stuff
        if 'file' not in request.files:
            print('No file found!')
            sys.exit("No File Found")
            return redirect(request.url)
        ufile = request.files['file']
        filename = ufile.filename
        if filename == '':
            print('No selected file')
            sys.exit("No selected file")
            return redirect(request.url)

        print('You got past all the checks!')
        target = os.path.join(STATIC, "temp/video/")
        print(target)

        if not os.path.isdir(target):
            os.mkdir(target)

        if ufile and allowed_file(filename):
            print(filename)
            destination = "/".join([target, filename])
            print(destination)
            ufile.save(destination)
            con.forward_split(STATIC + "/temp", filename)

    return render_template('select.html', img='static/temp/frames/', file=filename)

@app.route('/select_dims')
def select_dims():
    con.split_1(STATIC+'/temp', request.args.get('name'), request.args.get('init_frame'))
    tdims, pdims = con.estimate(STATIC + '/temp/frames/0.png')
    return render_template('process.html',
                            img='static/temp/frames/',
                            textdims=tdims,
                            picdims=pdims,
                            name=request.args.get('name'),
                            init=request.args.get('init_frame'),
                            end=request.args.get('end_frame'))



def send_csv(con, name, pdims, tdims, init, end, email):
    data = con.convert(name, pdims, tdims, init, end)
    ## Just a placeholder, will update to work properly on local machine when
    ## hosted
    print('done')
   # msg = MIMEMultipart()
   # msg['Subject'] = 'converted csv'
   # msg['From'] = 'mp4converter.threader@gmail.com'
   # body = 'DO NOT reply to this email, this account is only for sending out converted csv files'
   # content = MIMEText(body, 'plain')
   # msg.attach(content)
   # attachment = MIMEText(data)
   # attachment.add_header('Content-disposition','attachment',filename="".join((name[:-3],'csv')))
   # msg.attach(attachment)
   # s = smtplib.SMTP('smtp.gmail.com:587')
   # s.ehlo()
   # s.starttls()
   # s.login('mp4converter.threader@gmail.com', '...')
   # print(email)
   # s.sendmail('mp4converter.threader@gmail.com', email, msg.as_string())
   # s.quit()

@app.route('/process', methods=['POST','GET'])
def process():
    rarg = request.args.get
    def iarg(arg):
        return int(rarg(arg))
    tdims = [iarg('tcropx'), iarg('tcropy'), iarg('tcropx')+iarg('tcropw'),
                iarg('tcropy')+iarg('tcroph')]

    pdims = [iarg('pcropx'), iarg('pcropy'), iarg('pcropx')+iarg('pcropw'),
                iarg('pcropy')+iarg('pcroph')]
    args = [rarg('name'), pdims, tdims, rarg('init'), rarg('end')]
    #print('ACTIVE THREADS', threading.active_count())
    #pthread = threading.Thread(target=send_csv, args=(con, rarg('name'), pdims,
    #                                                  tdims, rarg('init'),
    #                                                  rarg('end'),
    #                                                  rarg('email'))))

    p = Process(target=send_csv, args=(con, rarg('name'), pdims, tdims,
                                       rarg('init'), rarg('end'),
                                       rarg('email')))
    p.start()

    # con.convert(rarg('name'), pdims, tdims, rarg('init'), rarg('end'))

    # tdims = [int(rarp['tcropx']), int(rarp['tcropy']), int(rarp['tcropx']) +
    #          int(rarp['tcropw']), int(rarp['tcropy']) + int(rarp['tcroph'])];
    # pdims = [int(rarp['pcropx']), int(rarp['pcropy']), int(rarp['pcropx']) +
    #          int(rarp['pcropw']), int(rarp['pcropy']) + int(rarp['pcroph'])];
    # print(rarp['filename'], pdims, tdims)
    #con.convert(rarp['filename'], pdims, tdims, rarp['init'])
    return redirect(url_for('index'))

@app.route('/_return_frames', methods=['GET'])
def retFrames():
    ret = ([int(f[:-4]) for f in os.listdir(STATIC+'temp/frames/') if f.endswith('.png')])
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

