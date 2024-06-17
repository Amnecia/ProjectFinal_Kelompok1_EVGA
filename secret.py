# user and admin
@app.route("/secret")
def secret():
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

            return render_template("secret.html", user_info=user_info)
        else:
            return redirect(url_for("home"))

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    

# admin only
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


