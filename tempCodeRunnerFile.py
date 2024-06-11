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
    print(produk)  # Add this line to check the produk variable
    return render_template('index.html', produk=produk)
    #token_receive = request.cookies.get("mytoken")
    #try:
     #   payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
    #except jwt.ExpiredSignatureError:
     #   return redirect(url_for("login", msg = "Your token has expired"))
    #except jwt.exceptions.DecodeError:
     #   return redirect(url_for("login", msg="There was a problem logging you in"))


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


@app.route('/editProduk/<_id>', methods=['GET'])
def edit_produk(_id):
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
        doc['gambar'] = image_name
        db.produk.update_one({'_id':ObjectId(_id)}, {'$set':doc})
    return render_template('edit_produk.html')



@app.route('/detail', methods=['GET'])
def detail_produk():
    return render_template('detail_produk.html')


@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        address = request.form['address']
        db.produk.find_one({'nama': nama, 'harga': harga, 'address': address})
        return redirect(url_for('status'))
    return render_template('order.html')

@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    token_receive = request.cookies.get("mytoken")
    try:
        # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # username = payload["id"]
        first_name_receive = request.form.get("firstName_give")
        last_name_receive = request.form.get("lastName_give")
        email_receive = request.form.get("email_give")
        address_receive = request.form.get("address_give")
        phone_number_receive = request.form.get("phoneNumber_give")
        password_receive = request.form.get("password_give")

        new_doc = {}
        if first_name_receive:
            new_doc["first_name"] = first_name_receive
        if last_name_receive:
            new_doc["last_name"] = last_name_receive
        if email_receive:
            new_doc["email"] = email_receive
        if address_receive:
            new_doc["address"] = address_receive
        if phone_number_receive:
            new_doc["phone_number"] = phone_number_receive
        if password_receive:
            password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
            new_doc["password"] = password_hash

        if new_doc:
            # db.users.update_one({"username": username}, {"$set": new_doc})
            return jsonify({"result": "success", "msg": "Profile updated!"})
        else:
            return jsonify({"result": "fail", "msg": "No data provided to update"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail", "msg": "Token expired or invalid"})

@app.route('/edit_etalase', methods=['POST'])
def edit_etalase():
    token_receive = request.cookies.get("mytoken")
    try:
        # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # username = payload["id"]

        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        new_doc = {}
        for i in range(1, 4):  # Loop through image1, image2, image3
            key = f'image{i}'
            if key in request.files:
                file = request.files[key]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    extension = filename.split(".")[-1]
                    file_path = f"etalase_{i}.{extension}"
                    file.save(os.path.join(upload_folder, file_path))
                    new_doc[f'image{i}'] = filename
                    new_doc[f'image{i}_real'] = os.path.join(upload_folder, file_path)

        # Here you can save new_doc to the database if needed

        return jsonify({"result": "success", "msg": "Files successfully uploaded"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


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