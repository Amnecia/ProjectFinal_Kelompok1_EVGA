from flask import Flask, redirect, url_for, render_template, request
from pymongo import MongoClient 
from bson import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime
import os


app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')



@app.route('/addProduk', methods=['GET'])
def tambah_produk():
    return render_template('tambah_produk.html')



@app.route('/editProduk', methods=['GET'])
def edit_produk():
    return render_template('edit_produk.html')



@app.route('/detail', methods=['GET'])
def detail_produk():
    return render_template('detail_produk.html')


@app.route('/order', methods=['GET'])
def order():
    return render_template('pesanan.html')



@app.route('/status', methods=['GET'])
def status():
    return render_template('status_pesanan.html')




@app.route('/list', methods=['GET'])
def list():
    return render_template('produk.html')




@app.route('/guest', methods=['GET'])
def guest():
    return render_template('guest.html')




@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)