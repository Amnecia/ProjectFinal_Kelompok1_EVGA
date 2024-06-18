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
#from dotenv import load_dotenv
import hashlib

#dotenv_path = join(dirname(__file__), '.env')
#load_dotenv(dotenv_path)

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

SECRET_KEY='EVGA'


TOKEN_KEY = 'mytoken'


@app.route('/')
def home():
    produk = db.produk.find()
    etalase_folder = 'static/assets/etalase/'
    etalase_images = [file for file in os.listdir(etalase_folder) if os.path.isfile(os.path.join(etalase_folder, file))]
    print(produk)  
    return render_template('index.html', produk=produk, etalase_images=etalase_images)



    
@app.route('/login', methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

@app.route("/get_role")
def get_role():
    token_receive = request.cookies.get(TOKEN_KEY)
    if not token_receive:
        return jsonify({"role": "guest"}), 200

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]
        
        user = db.users.find_one({"_id": ObjectId(id)}, {"_id": False})
        role = "user"
        if not user:
            user = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})
            role = "admin"

        if user:
            return jsonify({ 
                "role":role,
                "username" : user.get("username", "")
            })
        else:
            return jsonify({"role": "guest"}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"role": "guest"}), 200
    except jwt.exceptions.DecodeError:
        return jsonify({"role": "guest"}), 200

@app.route("/sign_in", methods=["POST"])
def sign_in():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    
    result = db.admin.find_one(
        {
            "email": email_receive,
            "password": pw_hash,
        }
    )
    
    if not result:
        result = db.users.find_one(
            {
                "email": email_receive,
                "password": pw_hash,
            }
        )
    
    if result:
        user_id = str(result["_id"])
        payload = {
            "id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        user_info = db.admin.find_one({"email": email_receive}, {"_id": False})
        if not user_info:
            user_info = db.users.find_one({"email": email_receive}, {"_id": False})
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({"result": "success", "token": token, "user_info": user_info})
    
    return jsonify({"result": "fail", "msg": "Login gagal, email atau password invalid"})


# def token_required(f):
#     def decorated_function(args,):
#         token = request.cookies.get(TOKEN_KEY)
#         if not token:
#             return redirect(url_for('login', msg='Login required'))

#         try:
#             data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
#             user_id = data['user_id']
#             current_user = db.users.find_one({'_id': ObjectId(user_id)})
#         except Exception as e:
#             return redirect(url_for('login', msg='Login required'))

#         return f(current_user, args, )
#     return decorated_function

# @app.route('/protected')
# @token_required
# def protected(current_user):
#     return f'Logged in as: {current_user["email"]}'
   


@app.route('/register', methods=['GET', 'POST'])
def register():
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
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]
        validasi = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})

        if validasi:
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
                    'today': mytime,
                }
                db.produk.insert_one(doc)
                return jsonify({'message': 'Product added successfully'})
            return render_template('tambah_produk.html')
        else:
            return redirect(url_for("home"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


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

@app.route('/etalase', methods=['GET'])
def Etalase():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]

        validasi = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})

        if validasi:
            user_info = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})

            return render_template("edit_etalase.html", user_info=user_info)
        else :
            return redirect(url_for("home"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/secret")
def secret():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        email = payload["id"]
        user = db.users.find_one({"email": email}, {"_id": False})
        if not user:
            user = db.admin.find_one({"email": email}, {"_id": False})

        if user:
            user_info = db.users.find_one({"email": email}, {"_id": False})
            if not user_info:
                user_info = db.admin.find_one({"email": email}, {"_id": False})

            return render_template("secret.html", user_info=user_info)
        else:
            return redirect(url_for("home"))

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))






@app.route('/detail/<_id>', methods=['GET'])
def detail_produk(_id):
    produk = db.produk.find_one({'_id': ObjectId(_id)})
    return render_template('detail_produk.html', produk=produk)

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        try:
            product_id = ObjectId(request.form['product_id'])
            quantity = int(request.form['quantity'])
            email = request.form['email']
            address = request.form['address']
            price = int(request.form['price'])
            date = datetime.strptime(request.form['date'], '%Y-%m-%d %H:%M:%S')

            order_data = {
                'product_id': product_id,
                'quantity': quantity,
                'email': email,
                'address': address,
                'price': price * quantity,
                'date': date
            }

            db.orders.insert_one(order_data)
            return redirect(url_for('status_pesanan'))
        except ValueError:
            # Handle invalid form data
            flash('Invalid form data')
            return render_template('order.html')

    return render_template('order.html')

@app.route('/status_pesanan')
def status_pesanan():
    orders = db.orders.find().sort('_id', -1)
    orders_with_email = [{'order_id': order['_id'], 'email': order['email'], 'product_name': order.get('product_name'), 'quantity': order['quantity'], 'address': order['address'], 'price': order['price'], 'date': order['date'], 'tatus': order.get('status')} for order in orders]
    return render_template('status_pesanan.html', orders=orders_with_email)

@app.route('/list', methods=['GET'])
def list():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]

        validasi = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})

        if validasi:
            produk = db.produk.find()

            return render_template('produk.html', produk=produk)
        else :
            return redirect(url_for("home"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/guest', methods=['GET'])
def guest():
    return render_template('guest.html')

@app.route('/profile', methods=['POST','GET'])
def profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]
        user = db.users.find_one({"_id": ObjectId(id)}, {"_id": False})
        if not user:
            user = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})

        if user:
            user_info = db.users.find_one({"_id": ObjectId(id)}, {"_id": False})
            if not user_info:
                user_info = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})

            return render_template("edit_profile.html", user_info=user_info)
        else:
            return redirect(url_for("home"))

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/get_profile")
def get_profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]
        
        user = db.users.find_one({"_id": ObjectId(id)}, {"_id": False})
        
        if not user:
            user = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})
        
        # If user is found, return the user information
        if user:
            return jsonify({
                "fullname": user.get("full_name"),
                "username": user.get("username"),
                "email": user.get("email"),
                "phone": user.get("contact_number"),
                "address": user.get("address")
            })
        else:
            return jsonify({"error": "User not found"}), 404
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"error": "Invalid token"}), 401


@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]
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
            update_user = db.users.update_one({"_id": ObjectId(id)}, {"$set": new_doc})
            update_admin = db.admin.update_one({"_id": ObjectId(id)}, {"$set": new_doc})
            
            if update_user.modified_count > 0 or update_admin.modified_count > 0:
                return jsonify({"result": "success", "msg": "Profile updated!"})
            else:
                return jsonify({"result": "fail", "msg": "No data provided to update or data unchanged"})
        else:
            return jsonify({"result": "fail", "msg": "No data provided to update"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



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

@app.route('/deleteproduk/<_id>', methods=['GET', 'POST'])
def deleteProduk(_id):
    id_receive = request.get("id_give")
    db.produk.delete_one({'_id': ObjectId(_id)})
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/form_ulasan', methods=['GET', 'POST'])
def form_ulasan_without_product():
    if request.method == 'POST':
        rating = request.form.get('rating')
        deskripsi = request.form.get('deskripsiProduk')

        # Simpan ulasan ke dalam database
        new_review = {
            'rating': rating,
            'deskripsi': deskripsi
        }
        db.produk.insert_one(new_review)  # Menyimpan ulasan ke dalam database

        return 'Ulasan berhasil disimpan'

    return render_template('form_ulasan.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)