#from cs50 import SQL
#import sqlite3
import os
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin

# # Instantiate Flask object named app
app = Flask(__name__)

# # Configure sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Creates a connection to the database
# db = SQL ( "sqlite:///data.sqlite" )
# db = sqlite3.connect('data.sqlite')
db = SQLAlchemy()
db.init_app(app)
app.config['SECRET_KEY'] = 'mysecret'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///C:\\Users\\Владислав\\PycharmProjects\\flask-ecomm\\data.sqlite'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_BINDS"] = {'data': 'sqlite:////C:\\Users\\Владислав\\PycharmProjects\\flask-ecomm\\data.sqlite'}
engine = create_engine('sqlite:///C:\\Users\\Владислав\\PycharmProjects\\flask-ecomm\\data.sqlite')



@app.route("/")
def index():
    shirts = engine.execute("SELECT * FROM shirts ORDER BY team ASC").fetchall()
    print(type(shirts))
    shirtsLen = len(shirts)
    # Initialize variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = engine.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team").fetchall()
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        shirts = engine.execute("SELECT * FROM shirts ORDER BY team ASC").fetchall()
        shirtsLen = len(shirts)
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ("index.html", shirts=shirts, shoppingCart=shoppingCart, shirtsLen=shirtsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)

@app.route("/account/")
def account():
    user = session['user']
    info = engine.execute("SELECT * from users where username = :user", user=user).fetchall()[1:]
    mail = info[5]
    fname = info[3]
    lname = info[4]
    return render_template("account.html", user=user, mail=mail, fname=fname, lname=lname)

@app.route("/buy/")
def buy():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        # Select info of selected shirt from database
        goods = engine.execute("SELECT * FROM shirts WHERE id = :id", id=id).fetchall()
        # Extract values from selected shirt record
        # Check if shirt is on sale to determine price
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        team = goods[0]["team"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        engine.execute("INSERT INTO cart (id, qty, team, image, price, subTotal) VALUES (:id, :qty, :team, :image, :price, :subTotal)", id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal)
        shoppingCart = engine.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team").fetchall()
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Select all shirts for home page view
        shirts = engine.execute("SELECT * FROM shirts ORDER BY team ASC").fetchall()
        shirtsLen = len(shirts)
        # Go back to home page
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/update/")
def update():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        engine.execute("DELETE FROM cart WHERE id = :id", id=id)
        # Select info of selected shirt from database
        goods = engine.execute("SELECT * FROM shirts WHERE id = :id", id=id).fetchall()
        # Extract values from selected shirt record
        # Check if shirt is on sale to determine price
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        team = goods[0]["team"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        engine.execute("INSERT INTO cart (id, qty, team, image, price, subTotal) VALUES (:id, :qty, :team, :image, :price, :subTotal)", id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal)
        shoppingCart = engine.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team").fetchall()
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Go back to cart page
        return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/filter/")
def filter():
    if request.args.get('continent'):
        query = request.args.get('continent')
        shirts = engine.execute("SELECT * FROM shirts WHERE continent = :query ORDER BY team ASC", query=query ).fetchall()
    if request.args.get('sale'):
        query = request.args.get('sale')
        shirts = engine.execute("SELECT * FROM shirts WHERE onSale = :query ORDER BY team ASC", query=query).fetchall()
    if request.args.get('id'):
        query = int(request.args.get('id'))
        shirts = engine.execute("SELECT * FROM shirts WHERE id = :query ORDER BY team ASC", query=query).fetchall()
    if request.args.get('kind'):
        query = request.args.get('kind')
        shirts = engine.execute("SELECT * FROM shirts WHERE kind = :query ORDER BY team ASC", query=query).fetchall()
    if request.args.get('price'):
        query = request.args.get('price')
        shirts = engine.execute("SELECT * FROM shirts ORDER BY onSalePrice ASC").fetchall()
    shirtsLen = len(shirts)
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        # Rebuild shopping cart
        shoppingCart = engine.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team").fetchall()
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Render filtered view
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    # Render filtered view
    return render_template ( "index.html", shirts=shirts, shoppingCart=shoppingCart, shirtsLen=shirtsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)

@app.route("/change_info", methods=['POST'])
def change():
    mail = request.form["mail"]
    fname = request.form["fname"]
    lname = request.form["lname"]


@app.route("/paying/", methods=['GET', 'POST'])
def shipping():
    order = engine.execute("SELECT * from cart").fetchall()
    for item in order:
        engine.execute("INSERT INTO purchases (uid, id, team, image, quantity) VALUES(:uid, :id, :team, :image, :quantity)", uid=session["uid"], id=item["id"], team=item["team"], image=item["image"], quantity=item["qty"] )
    engine.execute("DELETE from cart")
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    return render_template("paying.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )

@app.route("/checkout/")
def checkout():
    order = engine.execute("SELECT * from cart")
    delivery_cost = 20
    # Update purchase history of current customer
    #for item in order:
    #    engine.execute("INSERT INTO purchases (uid, id, team, image, quantity) VALUES(:uid, :id, :team, :image, :quantity)", uid=session["uid"], id=item["id"], team=item["team"], image=item["image"], quantity=item["qty"] )
    # Clear shopping cart
    # engine.execute("DELETE from cart")
    shoppingCart = []
    totItems, total, display = 0, 0, 0
    shopLen = len(shoppingCart)
    shoppingCart = engine.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team").fetchall()
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Redirect to home page
    total += delivery_cost
    return render_template ('shipping.html', shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/remove/", methods=["GET"])
def remove():
    # Get the id of shirt selected to be removed
    out = int(request.args.get("id"))
    # Remove shirt from shopping cart
    engine.execute("DELETE from cart WHERE id=:id", id=out)
    # Initialize shopping cart variables
    totItems, total, display = 0, 0, 0
    # Rebuild shopping cart
    shoppingCart = engine.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team").fetchall()
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Turn on "remove success" flag
    display = 1
    # Render shopping cart
    return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/new/", methods=["GET"])
def new():
    # Render log in page
    return render_template("new.html")


@app.route("/logged/", methods=["POST"] )
def logged():
    # Get log in info from log in form
    user = request.form["username"].lower()
    pwd = request.form["password"]
    #pwd = str(sha1(request.form["password"].encode('utf-8')).hexdigest())
    # Make sure form input is not blank and re-render log in page if blank
    if user == "" or pwd == "":
        return render_template("login.html")
    # Find out if info in form matches a record in user database
    query = "SELECT * FROM users WHERE username='" + user + "' AND password='" + pwd + "'"
    rows = engine.execute(query).fetchall()

    # If username and password match a record in database, set session variables
    if len(rows) == 1:
        session['user'] = user
        session['time'] = datetime.now( )
        session['uid'] = rows[0]["id"]
    # Redirect to Home Page
    if 'user' in session:
        return redirect("/")
    # If username is not in the database return the log in page
    return render_template("login.html", msg="Wrong username or password.")


@app.route("/history/")
def history():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Retrieve all shirts ever bought by current user
    myShirts = engine.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"]).fetchall()
    myShirtsLen = len(myShirts)
    # Render table with shopping history of current user
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myShirts=myShirts, myShirtsLen=myShirtsLen)


@app.route("/logout/")
def logout():
    # clear shopping cart
    engine.execute("DELETE from cart")
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register/", methods=["POST"] )
def registration():
    # Get info from form
    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    # See if username already in the database
    rows = engine.execute( "SELECT * FROM users WHERE username = :username ", username = username ).fetchall()
    # If username already exists, alert user
    if len( rows ) > 0:
        return render_template ( "new.html", msg="Username already exists!" )
    # If new user, upload his/her info into the users database
    new = engine.execute ( "INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
                    username=username, password=password, fname=fname, lname=lname, email=email )
    # Render login template
    return render_template ( "login.html" )


@app.route("/cart/")
def cart():
    if 'user' in session:
        # Clear shopping cart variables
        totItems, total, display = 0, 0, 0
        # Grab info currently in database
        shoppingCart = engine.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team").fetchall()
        # Get variable values
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    # Render shopping cart
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)


# @app.errorhandler(404)
# def pageNotFound( e ):
#     if 'user' in session:
#         return render_template ( "404.html", session=session )
#     return render_template ( "404.html" ), 404


# Only needed if Flask run is not used to execute the server
#if __name__ == "__main__":
#    app.run( host='0.0.0.0', port=8080 )
