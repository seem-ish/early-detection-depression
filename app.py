import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import firebase_admin
from firebase_admin import credentials,firestore
import pickle
from preprocess import preprocess
from werkzeug.utils import secure_filename
import os
import warnings
warnings.filterwarnings("ignore")

cred = credentials.Certificate('mypykey.json')
firebase_admin.initialize_app(cred)
fsdb = firestore.client()


app = Flask(__name__)       #Initialze flask constructor
app.config['UPLOAD_DIRECTORY'] = 'static/files'


#Add your own details
config = {
  "apiKey": "AIzaSyAqK3cVCo0q7-T_zfmPX-jWQgtnvgZ2Qrc",
  "authDomain": "try-proj-f6f6c.firebaseapp.com",
  "databaseURL": "",
  "storageBucket": "try-proj-f6f6c.appspot.com"
}

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

db = firebase.database()

#Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

#Login
@app.route("/")
def login():
    return render_template("index.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

#Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        doc_ref = fsdb.collection(u'uses').document(u'alovelace')
        doc_ref.set({
            u'email': person["email"],
            u'name': person["name"]
        })

        return render_template("welcome.html", email = person["email"], name = person["name"])
    else:
        return redirect(url_for('login'))

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]

            #Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            #Redirect to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

@app.route("/predict", methods=['POST'])
def predict():
    file = request.files['file']

    if file:
        flpath = os.path.join(
            app.config['UPLOAD_DIRECTORY'],
            secure_filename(file.filename)
        )
        file.save(flpath)

        X = preprocess(flpath)

        model_rc = pickle.load(open('models/random_classifier_model.pkl', 'rb'))
        prediction = model_rc.predict(X.reshape(1, -1))
        if prediction == 1:
            output = model_rc.predict_proba(X.reshape(1, -1))
            return render_template("welcome.html",prediction_text=f'The is a high probability - {output[0][1]} that you might be depressed',symptom_text= 'Looks like you are not getting enough activity',recommendation_text='Studies show that running just 5 to 10 minutes each day at a moderate pace may help reduce your risk of from heart attacks, strokes, and other common diseases. We suggest you to go for a run regularly')
        else:
            return render_template("welcome.html", prediction_text='You look in great shape')

    else:
        abort(400, "Error")


if __name__ == "__main__":
    app.run()