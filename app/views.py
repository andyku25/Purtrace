import os
import re
import requests

from flask import Flask, render_template, redirect, request, session, jsonify, flash, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField, StringField, PasswordField, SubmitField, DecimalField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email
from decimal import ROUND_UP
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
from flask_table import Table, Col

from app import app

# hexdicimal generater
import secrets

from .local_func import login_required, product_detail, dollar


db = SQLAlchemy(app)
print(app.config)

# Adding the dollar filter format to the jinja templates
app.jinja_env.filters["dollar"] = dollar

# Database tables
class Users(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    first_name = db.Column(db.String(60), unique=False, nullable=False)
    surname = db.Column(db.String(60), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    child = db.relationship('Profile', backref='user')

    def __repr__(self):
        return "<User %r>" % self.id


class Profile(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    prod_name = db.Column(db.String(100), unique=False, nullable=False)
    pur_price = db.Column(db.Float, unique=False, nullable=False)
    prod_cat = db.Column(db.String(30), unique=False, nullable=False)
    cat_oth = db.Column(db.String(40), unique=False, nullable=True)
    desc = db.Column(db.String(400), unique=False, nullable=True)
    add_date = db.Column(db.Date, unique=False, nullable=False)
    prod_img = db.Column(db.String(20), nullable=False, default='default.jpg')

    def __repr__(self):
        return "<Product %r>" % self.id


class AddProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(min=1, max=100)])
    price = DecimalField("Purchase Price", places=2, rounding=ROUND_UP, validators=[DataRequired()])
    category = SelectField("Category", coerce=str, choices=[("Camera Equipment", "Camera Equipment"), ("Electronics", "Electronics"), ("Kitchen Appliances", "Kitchen Appliances"), ("Sporting Gear", "Sporting Gear"), ("Other", "Other")])
    other = StringField("Other Category", validators=[Length(max=40)])
    description = TextAreaField("Description")
    purchase_date = DateField("Purchase Date", format='%Y-%m-%d', validators=[DataRequired()])
    image = FileField("Product Image", validators=[FileAllowed(['jpg', 'png'])])



def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, file_extention = os.path.splitext(form_image.filename)
    image_filename = random_hex + file_extention
    image_path = os.path.join(app.root_path, 'static/product_images/', image_filename)
    form_image.save(image_path)

    return image_filename

def delete_image(form_image):
    path_img = os.path.join(app.root_path, 'static/product_images/', form_image)
    return path_img


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        search = request.form.get("search")
        details = product_detail(search)

        if details == None:
            return "No products found"

        return render_template("results.html", products=details, search=search)
        
@app.route("/checker", methods=["GET", "POST"])
def checker():
    if request.method == "GET":
        return render_template("checker.html")
    else:
        search = request.form.get("search")
        details = product_detail(search)

        if details == None:
            return "No products found"

        return render_template("results.html", products=details, search=search)



@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = AddProductForm()
    
    # Post requests
    if form.validate_on_submit():
        product_name = form.name.data
        purchase_price = float(form.price.data)
        product_category = form.category.data
        description = form.description.data
        date_purchased = form.purchase_date.data
        product_image = form.image.data

        if product_image:
            image_file = save_image(product_image)

        user = Users.query.filter(Users.id == session["id"]).first()

        if product_image is None:
            if product_category == "Other":
                other_cat = form.other.data
                profile = Profile(prod_name=product_name, pur_price=purchase_price, prod_cat=product_category, cat_oth=other_cat, desc=description, add_date=date_purchased, user=user)
            else:
                profile = Profile(prod_name=product_name, pur_price=purchase_price, prod_cat=product_category, desc=description, add_date=date_purchased, user=user)

        else:
            if product_category == "Other":
                other_cat = form.other.data
                profile = Profile(prod_name=product_name, pur_price=purchase_price, prod_cat=product_category, cat_oth=other_cat, desc=description, add_date=date_purchased, prod_img=image_file, user=user)
            else:
                profile = Profile(prod_name=product_name, pur_price=purchase_price, prod_cat=product_category, desc=description, add_date=date_purchased, prod_img=image_file, user=user)

        try:
            db.session.add(profile)
            db.session.commit()
            print("done")
        except:
            return "Error adding product to template"

        flash("Product was Successfully Added", "success")
        return redirect(url_for('account'))

    # Get request
    else:
        return render_template("add.html", form=form)


@app.route("/results")
def results():
    return render_template("results.html")


@app.route("/dashboard")
@login_required
def account():
    products = Profile.query.filter(Profile.user_id == session["id"]).all()
    return render_template("dashboard.html", products=products)

@app.route("/edit_product/<string:id>", methods=["GET", "POST"])
@login_required
def edit(id):

    # query for the item that was selected for editing
    edit = Profile.query.filter(Profile.id==id).first()
    # pass in the product fields form
    form = AddProductForm()

    if request.method == "GET":
        
        # pass existing database date into the from values/data fields
        form.name.data = edit.prod_name
        form.price.data = edit.pur_price
        form.category.data = edit.prod_cat
        form.description.data = edit.desc
        form.purchase_date.data = edit.add_date

        # check other category
        if form.category.data == "Other":
            form.other.data = edit.cat_oth

    else:
        # Cancel action button
        if request.form.get('cancel'):
            return redirect(url_for('account'))

        # Posting update action
        if form.validate_on_submit():
            new_name = form.name.data
            new_price = float(form.price.data)
            new_category = form.category.data
            new_description = form.description.data
            new_purchase_date = form.purchase_date.data
            new_image = form.image.data

            if new_image:
                if edit.prod_img == "default.jpg":
                    pass
                else:
                    old_img = delete_image(edit.prod_img)
                    os.remove(old_img)
                
                updated_img = save_image(new_image)
                edit.prod_img = updated_img
            else:
                print("no new image uploaded")
                
            edit.prod_name = new_name
            edit.pur_price = new_price
            edit.prod_cat = new_category
            edit.desc = new_description
            edit.add_date = new_purchase_date

            if new_category == "Other":
                edit.cat_oth = form.other.data
            else:
                edit.cat_oth = None

            # Commit changes in the form for this product id
            db.session.commit()

            flash("Item has been Updated", "success")
            return redirect(url_for('account'))
    

    return render_template("edit.html", edit=edit, form=form)



@app.route("/delete_product/<string:id>", methods=["POST"])
@login_required
def delete_product(id):
    delete_prod = Profile.query.filter_by(id=id).first()
    
    # delete the img file from the static/product images folder that was saved if its not the default jpg
    if delete_prod.prod_img == "default.jpg":
        pass
    else:
        img_path = delete_image(delete_prod.prod_img)
        os.remove(img_path)

    # commit the removal of the product from the database
    db.session.delete(delete_prod)
    db.session.commit()

    flash("Product has been Deleted.", "success")

    return redirect(url_for('account'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # SELECT query to access database table
        users_table = Users.query.all()
        total_users = len(users_table)
        
        for user in range(total_users):
            print(users_table[user].first_name)

        return render_template("register.html", users_table=users_table)
    else:
        first_name = request.form.get("first_name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        username = request.form.get("username").lower()
        password = request.form.get("password")

        email_pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.[a-zA-Z]{2,4}$"

        if not first_name:
            return "Please enter First name"
        elif not surname:
            return "Please enter Last name"
        elif not email:
            return "please enter an Email Address"
        else:
            if re.search(email_pattern, email):
                if Users.query.filter(Users.email == email).first():
                    return "Email is already registered"
            else:
                return "invalid Email"

        if not username:
            return "please enter a username"
        
        if not password:
            return "Please enter a password"
        elif password != request.form.get("confirm_pass"):
            return "Passwords do not match"
        else:
            secure_pass = generate_password_hash(password)

        check_user = Users.query.filter(Users.username == username).first()
        if check_user:
            return "username is already taken"
        else:
            user = Users(first_name=first_name, surname=surname, email=email, username=username, password=secure_pass)
            
            try:
                db.session.add(user)
                db.session.commit()
                flash("User has been successfully registered", "success")
                return render_template("login.html")
            except:
                return "Error adding user to the database"

            query = Users.query.all()

            return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    else:
        username =  request.form.get("username").lower()
        pw = request.form.get("password")
        if not username:
            return "Please enter a username"
        elif not pw:
            return "please enter a password"
        
        user_pull = Users.query.filter(Users.username == username).first()
        if not user_pull or not check_password_hash(user_pull.password, pw):
            return "Username or password is incorrect"
        
        session["id"] = user_pull.id
        return redirect("/")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")