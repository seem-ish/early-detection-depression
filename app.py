from flask import Flask, redirect, render_template, request, session, abort, url_for
from firebase_admin import credentials, firestore, auth, storage
import firebase_admin
import os
import pickle
from preprocess import preprocess
from werkzeug.utils import secure_filename
from visualize import visualize

from google.oauth2 import service_account

import requests
import json

cred = credentials.Certificate('mypykey.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'try-proj-f6f6c.appspot.com'})
credentials = service_account.Credentials.from_service_account_file("mypykey.json")

FIREBASE_WEB_API_KEY = "AIzaSyAqK3cVCo0q7-T_zfmPX-jWQgtnvgZ2Qrc"
rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

app = Flask(__name__)  # Initialze flask constructor
app.config['UPLOAD_DIRECTORY'] = 'static/files'
app.config['UPLOAD_IMG'] = 'static/img'
# Home Page
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", header_text = "Depression Detection")


# After clicking on Join Us
@app.route("/signup")
def signup():
    return render_template("signup.html", header_text = "Depression Detection")

# After clicking on Login
@app.route("/loginpage")
def loginpage():
    return render_template("login.html", header_text = "Depression Detection")


# Initialze person as dictionary



@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":  # Only listen to POST
        form = request.form  # Get the data submitted
        global username
        username = form["name"]
        email = form["email"]
        password = form["password"]
        try:
            auth.create_user(display_name=username, email=email, password=password)
            payload = json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": True
            })
            r = requests.post(rest_api_url,
                              params={"key": FIREBASE_WEB_API_KEY},
                              data=payload)
            y = r.json()
            return render_template("welcome.html", header_text = f"Welcome, {username}!")
        except:
            return render_template("signup.html", header_text = "Depression Detection", existing_user="Email has been already used.")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":  # Only listen to POST
        form = request.form  # Get the data submitted
        email = form["email"]
        password = form["password"]
        try:
            payload = json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": True
            })
            r = requests.post(rest_api_url,
                              params={"key": FIREBASE_WEB_API_KEY},
                              data=payload)
            y = r.json()
            global username
            username = y['displayName']
            if "idToken" in y.keys():
                return render_template("welcome.html", header_text = f"Welcome, {username}!")
            else:
                return render_template("login.html",header_text = "Depression Detection", invalid_password="Invalid Password")
        except:
            return render_template("login.html",header_text = "Depression Detection", invalid_password="No user found")



@app.route("/predict", methods=['POST'])
def predict():
    file = request.files['file']

    if file:
        file_path = os.path.join(
            app.config['UPLOAD_DIRECTORY'],
            secure_filename(file.filename)
        )
        file.save(file_path)

        bucket = storage.bucket()  # storage bucket
        blob = bucket.blob(file_path)
        blob.upload_from_filename(file_path)

        # files = gstore.Client(credentials=credentials).list_blobs(
        #     storage.bucket().name)  # fetch all the files in the bucket
        # for i in files: print('The public url is ', i.public_url)

        X = preprocess(file_path)
        visualize(file_path)

        file_path = "static/img/fig1.png"

        bucket = storage.bucket()  # storage bucket
        blob = bucket.blob(file_path)
        blob.upload_from_filename(file_path)

        model_rc = pickle.load(open('models/random_classifier_model.pkl', 'rb'))
        prediction = model_rc.predict(X.reshape(1, -1))
        output = model_rc.predict_proba(X.reshape(1, -1))
        if prediction == 1:

            return render_template("welcome1.html", header_text = f"Welcome, {username}!",
                                   prediction_text=f'There is a high probability - {output[0][1]} that you might be depressed',
                                   symptom_text='Looks like you are not getting enough activity',
                                   recommendation_text='Studies show that running just 5 to 10 minutes each day at a moderate pace may help you. We suggest you to go for a run regularly.',
                                   img_src="../static/img/fig1.png")
        else:
            return render_template("welcome1.html", header_text = f"Welcome, {username}!", prediction_text='You look in great shape, keep it up!',
                                   symptom_text='Your activity chart shows that you are getting enough activity',
                                   img_src="../static/img/fig1.png")

    else:
        abort(400, "Error")


if __name__ == "__main__":
    app.run()
