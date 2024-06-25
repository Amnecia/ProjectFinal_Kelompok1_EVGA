import os
from os.path import join, dirname
from pymongo import MongoClient
import requests
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime  import datetime, timedelta
import jwt
from bson import ObjectId

#from dotenv import load_dotenv
import hashlib
'''
#dotenv_path = join(dirname(__file__), '.env')
#load_dotenv(dotenv_path)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)



MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
'''
app = Flask(__name__)

#client = MongoClient('mongodb+srv://andreasrafaeltobing:ManhwaXL9LUL@cluster0.aajaqnf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
#db = client.dbsandreasrafaeltobing

client = MongoClient('mongodb+srv://ade:adesaef@cluster0.lqterof.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.projekTA


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["UPLOAD_FOLDER"] = "static/assets/ProfilePicture"

SECRET_KEY='EVGA'


TOKEN_KEY = 'mytoken'


@app.route('/')
def home():
    produk = db.produk.find()
    etalase_folder = 'static/assets/etalase/'
    etalase_images = [file for file in os.listdir(etalase_folder) if os.path.isfile(os.path.join(etalase_folder, file))]

    produk_with_review_count_and_rating = []
    for p in produk:
        review_count = db.reviews.count_documents({'produk_id': str(p['_id'])})
        reviews = db.reviews.find({'produk_id': str(p['_id'])})
        ratings = [review['rating'] for review in reviews]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        p['review_count'] = review_count
        p['average_rating'] = average_rating
        produk_with_review_count_and_rating.append(p)

    return render_template('index.html', produk=produk_with_review_count_and_rating, etalase_images=etalase_images)


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



#@app.route('/forget_password', methods=['POST'])
#def forgot_password():
    email_receive = request.form["email_give"]
    user = db.users.find_one({
        "email": email_receive
        })
    if user:
        token = secret.token_hex(16)
        user.update({
            "password_reset_token": token
            })
        db.users.save(user)
        send_password_reset_email(
             email_receive, 
             token,
            )
        return jsonify({
            "result": "success", 
            "msg": "Password reset link sent to your email"
            })
    else:
        return jsonify({"result": "fail", "msg": "Email not found."})
    
    

#@app.route('/reset_password', methods=['POST'])
#def reset_password():
    token_receive = request.form["token_give"]
    new_password_receive = request.form["new_password_give"]
    user = db.users.find_one({"password_reset_token": token_receive})
    if user:
        pw_hash = hashlib.sha256(new_password_receive.encode("utf-8")).hexdigest()
        user.update({"password": pw_hash, "password_reset_token": ""})
        db.users.save(user)
        return jsonify({
            "result": "success", 
            "msg": "Password reset successfully"
            })
    else:
        return jsonify({"result": "fail", "msg": "Invalid token."})

#def send_password_reset_email(email, token):
    # Implement your email sending logic here
    #pass


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
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]
        validasi = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})

        if validasi:
            produk = db.produk.find_one({'_id': ObjectId(_id)})
            if produk:
                nama = request.form['nama']
                harga = request.form['harga']
                deskripsi = request.form['deskripsi']

                image1 = request.files['image1']
                image2 = request.files['image2']
                image3 = request.files['image3']

                if not nama or not harga or not deskripsi:
                    return jsonify({'message': 'Please fill in all fields'}), 400

                if not image1 or not image2 or not image3:
                    return jsonify({'message': 'Please upload all images'}), 400

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
                db.produk.update_one({'_id': ObjectId(_id)}, {'$set': doc})
                return jsonify({'message': 'Product has been updated successfully'})
            return jsonify({'message': 'Product not found'}), 404
        else:
            return redirect(url_for("home"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    except Exception as e:
        return jsonify({'message': 'Error updating product: ' + str(e)}), 500
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
    
@app.route('/submit_review/<_id>', methods=['POST'])
def submit_review(_id):
    produk = db.produk.find_one({'_id': ObjectId(_id)})
    if produk:
        rating = request.form['rating']
        review_text = request.form['deskripsiProduk']

        token_receive = request.cookies.get(TOKEN_KEY)
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_id = payload["id"]
            user = db.users.find_one({"_id": ObjectId(user_id)}, {"_id": False})
            if not user:
                user = db.admin.find_one({"_id": ObjectId(user_id)}, {"_id": False})

            if user:
                username = user.get("username")
                profile_picture = user.get("profile_picture")  # Get the profile picture from the user document

                today = datetime.now()
                mytime = today.strftime('%Y-%m-%d %H:%M')
                review = {
                    'produk_id': _id,
                    'rating': int(rating),
                    'review_text': review_text,
                    'username': username,
                    'profile_picture_url': user.get("profile_picture_url"),  # Store the profile picture URL
                    'today': mytime,
                }
                db.reviews.insert_one(review)
                # Redirect the user to the product detail page
                return redirect(url_for('detail_produk', _id=_id))
            else:
                return 'Error: User not found', 404
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return 'Error: Invalid token', 401
    return 'Error: Product not found', 404


# @app.route('/detail/<_id>', methods=['GET'])
# def detail_produk(_id):
#     produk = db.produk.find_one({'_id': ObjectId(_id)})
#     reviews = db.reviews.find({'produk_id': _id}) 
#     print(reviews)  # Query reviews based on produk_id
#     total_rating = 0
#     review_count = 0

#     for review in reviews:
#         total_rating += review['rating']
#         review_count += 1

#     if review_count > 0:
#         average_rating = total_rating / review_count
#     else:
#         average_rating = 0

#     return render_template('detail_produk.html', produk=produk, id=_id, average_rating=average_rating, review_count=review_count, reviews=reviews)
@app.route('/detail/<_id>', methods=['GET'])
def detail_produk(_id):
    produk_id = ObjectId(_id)

    produk = db.produk.find_one({'_id': produk_id})
    if not produk:
        return "Product not found", 404  # Return a 404 Not Found response if the product does not exist

    reviews_cursor = db.reviews.find({'produk_id': _id})
    reviews = [review for review in reviews_cursor]  # Convert the cursor to a list

    total_rating = 0
    review_count = len(reviews)

    for review in reviews:
        total_rating += review.get('rating', 0)

    if review_count > 0:
        average_rating = total_rating / review_count
    else:
        average_rating = 0

    # Fetch reviews with profile pictures
    reviews_with_pictures = []
    for review in reviews:
        profile_picture_url = get_profile_picture_url(review)
        reviews_with_pictures.append({
            'username': review['username'],
            'profile_picture_url': profile_picture_url,
            'rating': review['rating'],
            'review_text': review['review_text'],
            'today': review['today']
        })

    return render_template('detail_produk.html', produk=produk, id=_id, average_rating=average_rating, review_count=review_count, reviews=reviews_with_pictures)

def get_profile_picture_url(review):
    if review.get('profile_picture'):
        return url_for("static", filename=f"assets/ProfilePicture/{review['profile_picture']}", _external=True)
    else:
        return url_for("static", filename="assets/ProfilePicture/placeholder.png", _external=True)
    

@app.route('/cart', methods=['GET'])
def cart():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            id_user = payload["id"]
            user = db.users.find_one({'_id': ObjectId(id_user)})
            email = user["email"]
            cart_items = db.carts.find({"email":email})
            test = [item for item in cart_items]

            return render_template('order.html',cart_items=test)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/remove_item', methods=['POST'])
def remove_item():
    item_id = request.json.get('item_id')
    if not item_id:
        return jsonify({'result': 'error', 'message': 'Invalid item ID'}), 400

    try:
        db.carts.delete_one({'_id': ObjectId(item_id)})
        return jsonify({'result': 'success'})
    except Exception as e:
        return jsonify({'result': 'error', 'message': str(e)}), 500


@app.route('/order', methods=['POST'])
def order():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id_user = payload["id"]
        product_id = request.form['productId']
        quantity = int(request.form['quantity'])

        # Retrieve user and product details
        user = db.users.find_one({"_id": ObjectId(id_user)}, {"_id": False})
        product = db.produk.find_one({"_id": ObjectId(product_id)}, {"_id": False})

        if user and product:
            email = user["email"]
            address = user.get('address', 'No address provided')
            harga = int(product["harga"])
            product_name = product["nama"]

            # Check if the product is already in the cart
            cek_same = db.carts.find_one({"product_id": product_id, "email": email})
            if cek_same:
                # Update the existing quantity
                current_quantity = int(cek_same["quantity"])
                add_quantity = current_quantity + quantity
                db.carts.update_one({"product_id": product_id, "email": email}, {"$set": {"quantity": add_quantity}})
            else:
                # Insert a new cart entry
                order_data = {
                    'product_id': product_id,
                    'nama': product_name,
                    'quantity': quantity,
                    'email': email,
                    'harga': harga,
                    'address': address,
                }
                db.carts.insert_one(order_data)

            return jsonify({"success": True, "message": "Order placed successfully!"}), 200

        return jsonify({"success": False, "message": "User or product not found!"}), 404

    except jwt.ExpiredSignatureError:
        return redirect(url_for("home"))
    except jwt.DecodeError:
        return redirect(url_for("home"))
    except Exception as e:
        # Log the detailed error message
        app.logger.error(f"Error processing order: {str(e)}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

    


@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.json
    orders = data.get('orders', [])
    
    if not orders:
        return jsonify({'result': 'error', 'message': 'No orders selected.'}), 400

    # Calculate the total price
    total_price = sum(order['harga'] * order['quantity'] for order in orders)

    # Prepare the order data to be inserted
    order_data = {
        '_id': ObjectId(),  # Automatically generate an ObjectId
        'orders': orders,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Add the current date and time
        'status': 'is being prepared',  # Set the default status
        'total': total_price  # Calculate and add the total price
    }

    # Insert the order data into the database
    result = db.orders.insert_one(order_data)

    if result.inserted_id:
        # Extract orderIds from the orders to delete from carts
        order_ids = [order['orderId'] for order in orders]

        # Delete the items from the carts collection
        db.carts.delete_many({'orderId': {'$in': order_ids}})
        
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'error', 'message': 'Failed to save order.'}), 500

@app.route('/status_pesanan')
def get_orders():
    token_receive = request.cookies.get(TOKEN_KEY)
    if not token_receive:
        return jsonify({"error": "Missing token"}), 401

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    id_user = payload["id"]
    user = db.users.find_one({"_id": ObjectId(id_user)}, {"_id": False})
    email = user["email"]
    
    # Fetch orders based on email
    orders_data = db.orders.find({"orders.email": email})
    
    all_orders = []
    current_time = datetime.utcnow()

    for order_document in orders_data:
        order_date_str = order_document.get('date')
        status = order_document.get('status', 'Unknown')  # Default to 'Unknown' if status is missing
        
        # Add debug statement for order document
        print(f"Processing order document: {order_document}")

        if order_date_str:
            try:
                order_date = datetime.strptime(order_date_str, '%Y-%m-%d %H:%M')
                can_cancel = (current_time - order_date) < timedelta(minutes=15)
            except ValueError as e:
                print(f"Error parsing date '{order_date_str}': {e}")
                order_date = None
                can_cancel = False
        else:
            print("Order document missing 'date' field.")
            order_date = None
            can_cancel = False
        
        for order in order_document.get('orders', []):
            all_orders.append({
                '_id': order_document['_id'],
                'orders': order,
                'total': order_document.get('total', 0),
                'can_cancel': can_cancel,
                'status': status,
                'order_date': order_date_str  # Include raw date for debugging
            })
    
    grouped_orders = {}
    for order_group in all_orders:
        _id = str(order_group['_id'])
        if _id not in grouped_orders:
            grouped_orders[_id] = {
                'orders': [order_group['orders']],
                'total': order_group['total'],
                'can_cancel': order_group['can_cancel'],
                'status': order_group['status'],
                'order_date': order_group['order_date']  # Include raw date for debugging
            }
        else:
            grouped_orders[_id]['orders'].append(order_group['orders'])

    # Debug output to check what's being passed to the template
    print(f"Grouped Orders: {grouped_orders}")

    return render_template('status_pesanan.html', grouped_orders=grouped_orders)


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

@app.route("/upload_profile_picture", methods=["POST"])
def upload_profile_picture():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]
        
        file = request.files["profilePicture"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        
        db.users.update_one({"_id": ObjectId(id)}, {"$set": {"profile_picture": filename}})
        db.admin.update_one({"_id": ObjectId(id)}, {"$set": {"profile_picture": filename}})
        
        return jsonify({"result": "success", "msg": "Profile picture updated!"})
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
        profile_picture = request.files.get("profilePicture")

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

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            new_doc["profile_picture"] = filename

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
    
@app.route("/get_profile_picture")
def get_profile_picture():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        id = payload["id"]

        user = db.users.find_one({"_id": ObjectId(id)}, {"_id": False})
        if not user:
            user = db.admin.find_one({"_id": ObjectId(id)}, {"_id": False})

        if user:
            profile_picture = user.get("profile_picture")
            if profile_picture:
                profile_picture_url = url_for("static", filename=f"assets/ProfilePicture/{profile_picture}")
            else:
                # Return a placeholder image URL if profile picture is not found
                profile_picture_url = url_for("static", filename="assets/ProfilePicture/placeholder.png")
            return jsonify({"profile_picture_url": profile_picture_url})
        else:
            return jsonify({"error": "User not found"}), 404
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"error": "Invalid token"}), 401
    

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

@app.route('/setstatus', methods=['GET'])
def Set_status():
    token_receive = request.cookies.get(TOKEN_KEY)
    if not token_receive:
        return jsonify({"error": "Missing token"}), 401

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    # Fetch orders based on email
    orders_data = db.orders.find({})
    
    all_orders = []
    current_time = datetime.utcnow()

    for order_document in orders_data:
        order_date_str = order_document.get('date')
        status = order_document.get('status', 'Unknown')  # Default to 'Unknown' if status is missing
        
        # Add debug statement for order document
        print(f"Processing order document: {order_document}")

        if order_date_str:
            try:
                order_date = datetime.strptime(order_date_str, '%Y-%m-%d %H:%M')
                can_cancel = (current_time - order_date) < timedelta(minutes=15)
            except ValueError as e:
                print(f"Error parsing date '{order_date_str}': {e}")
                order_date = None
                can_cancel = False
        else:
            print("Order document missing 'date' field.")
            order_date = None
            can_cancel = False
        
        for order in order_document.get('orders', []):
            all_orders.append({
                '_id': order_document['_id'],
                'orders': order,
                'total': order_document.get('total', 0),
                'can_cancel': can_cancel,
                'status': status,
                'order_date': order_date_str  # Include raw date for debugging
            })
    
    grouped_orders = {}
    for order_group in all_orders:
        _id = str(order_group['_id'])
        if _id not in grouped_orders:
            grouped_orders[_id] = {
                'orders': [order_group['orders']],
                'total': order_group['total'],
                'can_cancel': order_group['can_cancel'],
                'status': order_group['status'],
                'order_date': order_group['order_date']  # Include raw date for debugging
            }
        else:
            grouped_orders[_id]['orders'].append(order_group['orders'])

    # Debug output to check what's being passed to the template
    print(f"Grouped Orders: {grouped_orders}")
    return render_template('list_pesanan.html', grouped_orders=grouped_orders)

@app.route('/update_status', methods=['POST'])
def update_status():
    # Get the document ID and new status from the form data
    document_id = request.form.get('order_id')
    new_status = request.form.get('status')
    print(document_id)
    print(new_status)

    if not document_id or not new_status:
        return jsonify({'error': 'Document ID and status are required'}), 400

    # Find and update the status of the document
    result = db.orders.update_one(
        {'_id': ObjectId(document_id)},  # Find the document by ObjectId
        {'$set': {'status': new_status}}  # Update the status field
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Order not found'}), 404

    return redirect(url_for('Set_status'))

@app.route('/deleteproduk/<_id>', methods=['GET', 'POST'])
def deleteProduk(_id):
    id_receive = request.form.get("id_give")
    db.produk.delete_one({'_id': ObjectId(_id)})
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/form_ulasan/<_id>', methods=['GET'])
def form_ulasan(_id):
    produk = db.produk.find_one({'_id': ObjectId(_id)})
    return render_template('form_ulasan.html', produk=produk)


@app.route('/get_reviews/<_id>', methods=['GET'])
def get_reviews(_id):
    reviews = db.reviews.find({'produk_id': _id})
    reviews_list = []
    for review in reviews:
        user = db.users.find_one({"_id": ObjectId(review['user_id'])}, {"_id": False})
        if user:
            profile_picture_url = url_for("static", filename=f"assets/ProfilePicture/{user.get('profile_picture')}", _external=True)
        else:
            profile_picture_url = url_for("static", filename="assets/ProfilePicture/placeholder.png", _external=True)
        reviews_list.append({
            'username': review['username'],
            'profile_picture_url': profile_picture_url,
            'rating': review['rating'],
            'review_text': review['review_text'],
            'today': review['today']
        })
    return jsonify({'reviews': reviews_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)