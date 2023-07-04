from cs50 import SQL 
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from functools import wraps
import os
import base64
from requests import post, get
import json



client_id = "0200f0f5702546fea9ba23537e65f695"
client_secret = "451dc6ccccb8428785e5992ae098d1fc"

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///users.db")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def get_token():
    aut_string = client_id + ":" + client_secret
    auth_bytes =  aut_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers = headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}



def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists..")
        return None
    

    return json_result[0]


def search_for_track(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_name}&type=track"

    query_url = url + query
    result = get (query_url, headers=headers)
    json_result = json.loads(result.content)['tracks']['items']
    return json_result


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


def get_album_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['items']
    return json_result


def get_songs_by_album(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['items']
    return json_result

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via post)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE name = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        
        # Remember which user has logged in 
        session["user_id"] = rows[0]["user_id"]

        # Redirect to the home page
        return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")





@app.route("/register", methods=["GET", "POST"])
def register():
    # POST method 
    if request.method == "POST":
        mail = request.form.get("mail")    
        password = generate_password_hash(request.form.get("password"))
        confirmation_password = request.form.get("password1")

        # Validation name 
        if not mail:
            return apology("Mail is requried!", 400)
        
        # Validation of passwords 
        if not password or not confirmation_password:
            return apology("Password or Confirmation password is left was not entered!", 400) 
        
        # Validation of matching passwords
        if not check_password_hash(password, confirmation_password):
            return apology("Passwords don't match!", 400)
    

        row = db.execute("SELECT name FROM user")
        if any(user["name"] == mail for user in row):
            return apology("username already exist", 403)
        else:
            db.execute("INSERT INTO user (name, password) VALUES(?, ?)", mail, password )
        # Adding user's information to database

        # Confirm registratrion
        return redirect("/login")
    else: 
        return render_template("register.html")




# Route to fetch songs by album ID
@app.route("/albums/<album_id>/songs", methods=["GET"])
def fetch_songs_by_album(album_id):
    # Logic to retrieve songs by album ID
    token = get_token()
    songs = get_songs_by_album(token, album_id)
    return jsonify(songs=songs)





# Route to search for an artist and get albums
@app.route("/search", methods=["POST"])
def search():
    if request.method == "POST":
        # Get artist name
        artist_name = request.form.get("artist")
        # get token
        token = get_token()
        # get artist result
        result = search_for_artist(token, artist_name)
        # get track name
        track_name =  request.form.get("track")
        # get track result
        tracks = search_for_track(token, track_name)
        artist_id = result['id']
        albums = get_album_by_artist(token, artist_id)
           
        return jsonify(result=result, albums=albums, tracks=tracks)
      



# Route for the home page
@app.route("/")
@login_required
def index():
    return render_template("index.html")



