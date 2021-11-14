import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
import time
import numpy as np
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'uploads'


@app.route('/')
def index():
    return render_template('index.html', file='',out='', time='')

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    c = int(request.form["n-K"])
    filename = secure_filename(uploaded_file.filename)
    out = ''
    if filename != '':
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        out, time = compressImage(filename,c)
    return render_template('index.html', file=filename, out=out, time=time)

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
    maxsteps = 1000
    while cond:
        val = matrix.dot(val)
        val, vec = np.linalg.qr(val)
        delta = val - val_
        deltaabs = delta ** 2
        error = deltaabs.sum()
        val_ = val
        step += 1
        # print(step)
        if step > maxsteps or error < toleransi:
            break
    
    return val, np.sqrt(np.diag(vec))

def svd(matriks):
    kiri,_ = igen(matriks @ matriks.T)
    kanan,S= igen(matriks.T @ matriks)
    return kiri, S, kanan.T

def normalize(x):
    fac = abs(x).max()
    x_n = x / x.max()
    return fac, x_n


def compressImage(file, c):
    imge = Image.open(os.path.join(app.config['UPLOAD_PATH'], file))
    start = time.time()
    if (imge.mode =='L'):
        img = np.asarray(imge).astype(float)
        N = min(img.shape)
        k = (c * N) // 100
        u, s, v = svd(img)
        rimg = np.dot(u[:,:k],np.dot(np.diag(s[:k]),v[:k,:]))
    else:
        imge = imge.convert("RGB")
        img = np.asarray(imge).astype(float)
        r = img[:,:,0]
        g = img[:,:,1]
        b = img[:,:,2]
        N = min(r.shape)
        k = (c * N) // 100
        print("start")
        #dah diganti
        ur,sr,vr = svd(r)
        print("red selsai")
        ug,sg,vg = svd(g)
        print("green selesai")
        ub,sb,vb = svd(b) 
        print("blue selsai")
        rr = np.dot(ur[:,:k],np.dot(np.diag(sr[:k]), vr[:k,:])) 
        rg = np.dot(ug[:,:k],np.dot(np.diag(sg[:k]), vg[:k,:]))
        rb = np.dot(ub[:,:k],np.dot(np.diag(sb[:k]), vb[:k,:]))
        #merging
        rimg = np.zeros(img.shape)
        rimg[:,:,0] = rr
        rimg[:,:,1] = rg
        rimg[:,:,2] = rb
        rimg = np.clip(rimg,0,255).astype(np.uint8)
        
    durasi = time.time() - start
    compressed_image = Image.fromarray(rimg)
    compressed_image.save(os.path.join(app.config['UPLOAD_PATH'], ("compressed_"+file)))
    return "compressed_"+file, durasi

