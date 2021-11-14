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

# fungsi cari igen value 

def igen(matrix):
    M, N = matrix.shape
    val = np.random.rand(M, N)
    val, rd = np.linalg.qr(val)
    val_ = val
    a = np.array(matrix)
    toleransi = 1e-5
    error = 1
    cond =True
    step = 0
    maxsteps = 500
    while cond:
        val = matrix.dot(val)
        val, vec = np.linalg.qr(val)
        delta = val - val_
        deltaabs = delta ** 2
        error = deltaabs.sum()
        val_ = val
        step += 1
        if step > maxsteps and error < toleransi:
            break
    
    return val, np.diag(vec)



def normalize(x):
    fac = abs(x).max()
    x_n = x / x.max()
    return fac, x_n


def compressImage(file):
    imge = Image.open(os.path.join(app.config['UPLOAD_PATH'], file))
    img = np.asarray(imge).astype(float)
    r = img[:,:,0]
    g = img[:,:,1]
    b = img[:,:,2]
    N = min(r.shape)
    k = round(0.01 * N)
    rows = len(r)
    cols = len(r[0])

    # kali transpose sm matrix awal
    mulr = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*r)] for X_row in r.transpose()]
    mulg = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*g)] for X_row in r.trasnpose()]
    mulb = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*b)] for X_row in r.transpose()]

    igen(mulr)

    


    

    #!skrg masi pake numpy ntr diganti
    # ur,sr,vr = np.linalg.svd(r)
    # ug,sg,vg = np.linalg.svd(g)
    # ub,sb,vb = np.linalg.svd(b) 
    # rr = np.dot(ur[:,:k],np.dot(np.diag(sr[:k]), vr[:k,:])) 
    # rg = np.dot(ug[:,:k],np.dot(np.diag(sg[:k]), vg[:k,:]))
    # rb = np.dot(ub[:,:k],np.dot(np.diag(sb[:k]), vb[:k,:]))
        
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

