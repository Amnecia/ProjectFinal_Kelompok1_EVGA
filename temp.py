@app.route('/guest_order', methods=['POST'])
def add_to_cart():
    product_id = ObjectId(request.form['productId'])
    quantity = int(request.form['quantity'])
    id_cart = request.cookies.get(CART_KEY)

    if not id_cart:
        id_cart = str(ObjectId())  # Generate a unique cart ID if it doesn't exist
        new_cart = True
    else:
        new_cart = False
    
    cart_data = {
        'id_cart': id_cart,
        'product_id': product_id,
        'quantity': quantity,
    }

    db.guest_carts.insert_one(cart_data)

    return jsonify({"result": "success", "new_cart": new_cart, "id_cart": id_cart})