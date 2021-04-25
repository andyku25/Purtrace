# Purtrace: A CS50 Final Project

This is a web application designed to allow users to search for any product (currently only linked to Best Buy products API) and return the Name, Price, Sale Price, and images of the first 20 results. There is also the functionality for the user to register and login to their profile. Benefits to having their own profile is the ability to view, add, edit and delete any products that the users own to a database that only they can have access to. This allows users to keep track of their possessions and have a record saved in case the item is lost, stolen, sold, or disposed of. 

## Technologies used:
* Backend:
    * Python 3.8: Flask Web framework
* Database:
    * sqlite
* Frontend:
    * HTML
    * CSS
    * Javascript

## Package Dependencies
```
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
from functools import wraps

# hexdicimal generater
import secrets
```


## Key Functions
* Search field for products that are part of the suite of offerings at BestBuy ranging from electronics to home appliances.
* Product ownership list with forms to add, update/edit, or delete records unique to users profile

## Demo


> ![Search functionality](https://raw.githubusercontent.com/andyku25/Purtrace/master/search.gif)
### Profile Ownership List example
> ![Screenshot](https://github.com/andyku25/Purtrace/blob/master/static/ownerlist_example.jpg?raw=true)

## Running application.py 
Use the virtual environment by running the terminal line below
```
pipenv run python application.py
```