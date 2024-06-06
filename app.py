import os
from os.path import join, dirname


from pymongo import MongoClient
import requests
import requests
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)


client = MongoClient('mongodb+srv://andreasrafaeltobing:ManhwaXL9LUL@cluster0.aajaqnf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.dbsandreasrafaeltobing

app.config['TEMPLATES_AUTO_RELOAD'] = True


SECRET_KEY='PLACEHOLDER_RANDOM'



TOKEN_KEY = 'mytoken'

@app.route('/')
def home():
    #token_receive = request.cookies.get("mytoken")
    #try:
     #   payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
    #except jwt.ExpiredSignatureError:
     #   return redirect(url_for("login", msg = "Your token has expired"))
    #except jwt.exceptions.DecodeError:
     #   return redirect(url_for("login", msg="There was a problem logging you in"))
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    msg = request.args.get("msg")
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')



@app.route('/addProduk', methods=['GET', 'POST'])
def tambah_produk():
    if request.method=='POST':
        nama = request.form['nama']
        harga = request.form['harga']
        deskripsi = request.form['deskripsi']
        image = request.files['image']
        extension=image.filename.split('.')[-1]
        today=datetime.now()
        mytime=today.strftime('%Y-%M-%d-%H-%m-%S') 
        image_name=f'image-{mytime}.{extension}'
        save_to=f'static/assets/productImage/{image_name}'
        image.save(save_to)
        doc={
            'nama' :nama,
            'harga':harga,
            'deskripsi': deskripsi,
            'image': image_name,
        }
        db.produk.insert_one(doc)
    return render_template('tambah_produk.html')


@app.route('/editProduk', methods=['GET'])
def edit_produk():
    return render_template('edit_produk.html')



@app.route('/detail', methods=['GET'])
def detail_produk():
    return render_template('detail_produk.html')


@app.route('/order', methods=['GET'])
def order():
    return render_template('order.html')



@app.route('/status', methods=['GET'])
def status():
    return render_template('status_pesanan.html')




@app.route('/list', methods=['GET'])
def list():
    return render_template('produk.html')




@app.route('/guest', methods=['GET'])
def guest():
    return render_template('guest.html')



@app.route('/setstatus', methods=['GET'])
def SetStatus():
    return render_template('set_status.html')



@app.route('/etalase', methods=['GET'])
def etalase():
    return render_template('edit_etalase.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)