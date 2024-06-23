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

#dotenv_path = join(dirname(__file__), '.env')
#load_dotenv(dotenv_path)

app = Flask(__name__)

#client = MongoClient('mongodb+srv://ade:adesaef@cluster0.lqterof.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
#db = client.projekTA

client = MongoClient('mongodb+srv://ade:adesaef@cluster0.lqterof.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.projekTA
email = 'user'

def cart():
    db.orders.update_one(
        {'_id': ObjectId('6676c167a8b94f0f7bdfa267')},  # Find the document by ObjectId
        {'$set': {'status': 'new_status'}}  # Update the status field
    )

cart()