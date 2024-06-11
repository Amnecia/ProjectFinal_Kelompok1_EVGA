import os
from os.path import join, dirname
from pymongo import MongoClient
import requests
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from bson import ObjectId

app = Flask(__name__)

client = MongoClient('mongodb+srv://andreasrafaeltobing:ManhwaXL9LUL@cluster0.aajaqnf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.dbsandreasrafaeltobing

app.config['TEMPLATES_AUTO_RELOAD'] = True

SECRET_KEY='PLACEHOLDER_RANDOM'

TOKEN_KEY = 'mytoken'

@app.route('/')
def home():
    produk = db.produk.find()
    print(produk)  
    return render_template('index.html', produk=produk)



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
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        deskripsi = request.form['deskripsi']
        image1 = request.files['image1']
        image2 = request.files['image2']
        image3 = request.files['image3']

        extension1 = image1.filename.split('.')[-1]
        extension2 = image2.filename.split('.')[-1]
        extension3 = image3.filename.split('.')[-1]

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d %H:%M')

        image_name1 = f'image1-{mytime}.{extension1}'
        image_name2 = f'image2-{mytime}.{extension2}'
        image_name3 = f'image3-{mytime}.{extension3}'

        save_to1 = f'static/assets/productImage/{image_name1}'
        save_to2 = f'static/assets/productImage/{image_name2}'
        save_to3 = f'static/assets/productImage/{image_name3}'

        image1.save(save_to1)
        image2.save(save_to2)
        image3.save(save_to3)

        doc = {
            'nama': nama,
            'harga': harga,
            'deskripsi': deskripsi,
            'image1': image_name1,
            'image2': image_name2,
            'image3': image_name3,
            'today': mytime,  # Add this line to record the creation date and time
        }
        db.produk.insert_one(doc)
        return jsonify({'message': 'Product added successfully'})
    return render_template('tambah_produk.html')

@app.route('/editProduk/<_id>', methods=['GET'])
def edit_produk(_id):
    produk = db.produk.find_one({'_id': ObjectId(_id)})
    return render_template('edit_produk.html', produk=produk)

@app.route('/updateProduk/<_id>', methods=['POST'])
def update_produk(_id):
    produk = db.produk.find_one({'_id': ObjectId(_id)})
    if produk:
        nama = request.form['nama']
        harga = request.form['harga']
        deskripsi = request.form['deskripsi']
        image1 = request.files['image1']
        image2 = request.files['image2']
        image3 = request.files['image3']

        extension1 = image1.filename.split('.')[-1]
        extension2 = image2.filename.split('.')[-1]
        extension3 = image3.filename.split('.')[-1]

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d %H:%M')

        image_name1 = f'image1-{mytime}.{extension1}'
        image_name2 = f'image2-{mytime}.{extension2}'
        image_name3 = f'image3-{mytime}.{extension3}'

        save_to1 = f'static/assets/productImage/{image_name1}'
        save_to2 = f'static/assets/productImage/{image_name2}'
        save_to3 = f'static/assets/productImage/{image_name3}'

        image1.save(save_to1)
        image2.save(save_to2)
        image3.save(save_to3)

        updated_fields = {
            'nama': nama,
            'harga': harga,
            'deskripsi': deskripsi,
            'image1': image_name1,
            'image2': image_name2,
            'image3': image_name3,
            'updated_at': datetime.now()
        }

        db.produk.update_one({'_id': ObjectId(_id)}, {'$set': updated_fields})
        return jsonify({'message': 'Product updated successfully'})
    return jsonify({'message': 'Product not found'}), 404

@app.route('/detail/<_id>', methods=['GET'])
def detail_produk(_id):
    produk = db.produk.find_one({'_id': ObjectId(_id)})
    return render_template('detail_produk.html', produk=produk)

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        address = request.form['address']
        db.produk.find_one({'nama': nama, 'harga': harga, 'address': address})
        return redirect(url_for('status'))
    return render_template('order.html')

@app.route('/status/<_id>', methods=['GET'])
def status(_id):
    produk = db.produk.find_one({'_id': ObjectId(_id)})
    return render_template('status_pesanan.html', produk=produk)

@app.route('/list', methods=['GET'])
def list():
    produk = db.produk.find()
    return render_template('produk.html', produk=produk)

@app.route('/guest', methods=['GET'])
def guest():
    return render_template('guest.html')

@app.route('/setstatus', methods=['POST'])
def SetStatus():
    status = request.form['status']
    _id = request.form['_id']
    db.produk.update_one({'_id': ObjectId(_id)}, {'$set': {'status': status}})
    return jsonify({'message': 'Status updated successfully'})

@app.route('/etalase', methods=['GET'])
def etalase():
    return render_template('edit_etalase.html')

@app.route('/deleteproduk/<_id>', methods=['GET', 'POST'])
def deleteProduk(_id):
    db.produk.delete_one({'_id': ObjectId(_id)})
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/form_ulasan/<_id>', methods=['GET', 'POST'])
def form_ulasan(_id):
    if request.method == 'POST':
        ulasan = request.form['ulasan']
        rating = request.form['rating']
        db.produk.update_one({'_id': ObjectId(_id)}, {'$set': {'ulasan': ulasan, 'rating': rating}})
        return jsonify({'message': 'Ulasan berhasil dikirim'})
    return render_template('form_ulasan.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)