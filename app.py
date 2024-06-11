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
from os.path import join, dirname
from dotenv import load_dotenv
import hashlib

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

# app.config['TEMPLATES_AUTO_RELOAD']=True
# app.config['UPLOAD_FOLDER']='./static/profile_pics'

# SECRET_KEY = 'SPARTA'

# MONGODB_URI = os.environ.get("MONGODB_URI")
# DB_NAME =  os.environ.get("DB_NAME")
# client = MongoClient(MONGODB_URI)
# db = client[DB_NAME]

# TOKEN_KEY = 'mytoken'

# client = MongoClient('mongodb+srv://andreasrafaeltobing:ManhwaXL9LUL@cluster0.aajaqnf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
# db = client.dbsandreasrafaeltobing

client = MongoClient('mongodb+srv://ade:adesaef@cluster0.lqterof.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.projekTA

app.config['TEMPLATES_AUTO_RELOAD'] = True

SECRET_KEY='PLACEHOLDER_RANDOM'

TOKEN_KEY = 'ytoken'


@app.route('/')
def home():
    produk = db.produk.find()
    etalase_folder = 'static/assets/etalase/'
    etalase_images = [file for file in os.listdir(etalase_folder) if os.path.isfile(os.path.join(etalase_folder, file))]
    return render_template('index.html', produk=produk, etalase_images=etalase_images)



    
@app.route('/login', methods=['GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashed_password(password)

        user = db.users.find_one({'email': email, 'password': hashed_password})
        if user:
            token = jwt.encode({
                'user_id': str(user['_id']),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, SECRET_KEY, algorithm='HS256')

            response = response(redirect(url_for('home')))
            response.set_cookie(TOKEN_KEY, token)
            return response
        else:
            msg = 'Invalid email or password'
            return render_template('login.html', msg=msg)
    return render_template('login.html')



@app.route('/logout')
def logout():
    response = response(redirect(url_for('login')))
    response.set_cookie(TOKEN_KEY, '', expires=0)
    return response

def token_required(f):
    def decorated_function(args,):
        token = request.cookies.get(TOKEN_KEY)
        if not token:
            return redirect(url_for('login', msg='Login required'))

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']
            current_user = db.users.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            return redirect(url_for('login', msg='Login required'))

        return f(current_user, args, )
    return decorated_function

@app.route('/protected')
@token_required
def protected(current_user):
    return f'Logged in as: {current_user["email"]}'
   


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        address = request.form['address']
        contact_number = request.form['contact_number']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        existing_user = db.users.find_one({"username": username})
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        new_user = {
            "full_name": full_name,
            "username": username,
            "address":address,
            "phone_number": contact_number,
            "email": email,
            "password": hashed_password
        }
        
        result = db.users.insert_one(new_user)
        user_id = str(result.inserted_id)
        
        token = jwt.encode(
            {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY, algorithm='HS256')
        
        return jsonify({'token': token.decode('UTF-8')})
    return render_template('register.html')


@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    full_name = request.form.get('full_name')
    username = request.form.get('username')
    address = request.form.get('address')
    contact_number = request.form.get('phoneNumber')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    
    if password != confirm_password:
        return 'Passwords do not match', 400

    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    new_user = {
        'full_name': full_name,
        'username': username,
        'address':address,
        'contact_number': contact_number,
        'email': email,
        'password': hashed_password
    }
    db.users.insert_one(new_user)
    return redirect(url_for('login'))
    
    

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

@app.route('/Etalase', methods=['GET'])
def Etalase():
    return render_template('edit_etalase.html')


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

@app.route('/profile', methods=['POST','GET'])
def profile():
    return render_template('edit_profile.html')

@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    # token_receive = request.cookies.get("mytoken")
    try:
        # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # username = payload["id"]
        full_name_receive = request.form.get("fullName_give")
        username_receive = request.form.get("username_give")
        email_receive = request.form.get("email_give")
        address_receive = request.form.get("address_give")
        phone_number_receive = request.form.get("phoneNumber_give")
        password_receive = request.form.get("password_give")

        new_doc = {}
        if full_name_receive:
            new_doc["full_name"] = full_name_receive
        if username_receive:
            new_doc["username"] = username_receive
        if address_receive:
            new_doc["address"] = address_receive
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
            db.users.update_one({"username": username_receive}, {"$set": new_doc})
            return jsonify({"result": "success", "msg": "Profile updated!"})
        else:
            return jsonify({"result": "fail", "msg": "No data provided to update"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail", "msg": "Token expired or invalid"})

from werkzeug.utils import secure_filename

@app.route('/get_images', methods=['GET'])
def get_images():
    app.config['etalase_folder'] = 'static/assets/etalase/'
    try:
        image_files = os.listdir(app.config['etalase_folder'])
        image_urls = [f'/static/assets/etalase/{file}' for file in image_files]
        return jsonify(image_urls=image_urls)
    except Exception as e:
        return jsonify(error=str(e))
    

@app.route('/edit_etalase', methods=['POST'])
def edit_etalase():
    etalase_folder = 'static/assets/etalase/'
    uploaded_files = request.files
    for i, file in enumerate(uploaded_files.values()):
        if file:
            filename = f'etalase{i + 1}.{secure_filename(file.filename).split(".")[-1]}'
            file_path = os.path.join(etalase_folder, filename)
            file.save(file_path)
    return jsonify({"message": "Images uploaded successfully"})


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