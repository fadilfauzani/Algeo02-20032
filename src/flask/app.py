import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename

import numpy as np
from numpy.linalg import norm
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'uploads'


@app.route('/')
def index():
    return render_template('index.html', file='',out='')

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    out = ''
    if (filename != ''):
        out = compressImage(filename)
    return render_template('index.html', file=filename, out=out)

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

def compressImage(file):
    imge = Image.open(os.path.join(app.config['UPLOAD_PATH'], file))
    img = np.asarray(imge).astype(float)
    r = img[:,:,0]
    g = img[:,:,1]
    b = img[:,:,2]
    N = min(r.shape)
    k = round(0.01 * N)

    #!skrg masi pake numpy ntr diganti
    ur,sr,vr = np.linalg.svd(r)
    ug,sg,vg = np.linalg.svd(g)
    ub,sb,vb = np.linalg.svd(b) 
    rr = np.dot(ur[:,:k],np.dot(np.diag(sr[:k]), vr[:k,:])) 
    rg = np.dot(ug[:,:k],np.dot(np.diag(sg[:k]), vg[:k,:]))
    rb = np.dot(ub[:,:k],np.dot(np.diag(sb[:k]), vb[:k,:]))
        
    #merging
    rimg = np.zeros(img.shape)
    rimg[:,:,0] = rr
    rimg[:,:,1] = rg
    rimg[:,:,2] = rb
        
    for ind1, row in enumerate(rimg):
        for ind2, col in enumerate(row):
            for ind3, value in enumerate(col):
                if value < 0:
                    rimg[ind1,ind2,ind3] = abs(value)
                if value > 255:
                    rimg[ind1,ind2,ind3] = 255
    compressed_image = rimg.astype(np.uint8)
    compressed_image = Image.fromarray(compressed_image)
    compressed_image.save(os.path.join(app.config['UPLOAD_PATH'], ("compressed_"+file)))
    return "compressed_"+file