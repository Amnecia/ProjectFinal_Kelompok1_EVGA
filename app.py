from flask import Flask, redirect, url_for, render_template, request, jsonify
from pymongo import MongoClient 
from bson import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from os.path import join, dirname
from dotenv import load_dotenv
import hashlib
import jwt

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

# app.config['TEMPLATES_AUTO_RELOAD']=True
# app.config['UPLOAD_FOLDER']='./static/profile_pics'

# SECRET_KEY = 'SPARTA'

# MONGODB_URI = os.environ.get("MONGODB_URI")
# DB_NAME =  os.environ.get("DB_NAME")
# client = MongoClient(MONGODB_URI)
# db = client[DB_NAME]

# TOKEN_KEY = 'mytoken'

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

@app.route('/editEtalase', methods=['GET'])
def edit_etalase():
    return render_template('edit_etalase.html')


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

@app.route('/profile', methods=['POST','GET'])
def profile():
    return render_template('edit_profile.html')

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

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')



@app.route('/setstatus', methods=['GET'])
def SetStatus():
    return render_template('set_status.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)