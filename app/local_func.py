from functools import wraps
from flask import session, redirect, request
import requests
from app import app


import os

# Keys
# bb_key="MhxYJnsKWeVr9Q8gUphMIpG2"
print(app.config["BB_API_KEY"])
bb_key = app.config["BB_API_KEY"]


def login_required(f):
    @wraps(f)
    def decord_routes(*args, **kwargs):
        if session.get("id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decord_routes

def product_detail(criteria):
    bb_link = "https://api.bestbuy.com/v1/products((search={}))?format=json&pageSize=20&apiKey={}".format(criteria, bb_key)

    response = requests.get(bb_link)
    try:
        prod_json = response.json()
        results = prod_json["products"]

        result_list = []

        for result in results:
            dictionary = {
                "name": result["name"],
                "price": result["regularPrice"],
                "salePrice": result["salePrice"],
                "source": result["source"],
                "image": result["image"],
                "url": result["url"]
            }
            result_list.append(dictionary)
            
        # print(result_list)

        return result_list
        # return {
        #     "name": product_prop["name"],
        #     "price": product_prop["regularPrice"],
        #     "salePrice": product_prop["salePrice"],
        #     "source": product_prop["source"],
        #     "image": product_prop["image"]
        # }
    except (KeyError, TypeError, ValueError, IndexError):
        return None

def dollar(value):
    return f"${value:,.2f}"


