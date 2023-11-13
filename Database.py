from flask import *
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from datetime import datetime
from io import BytesIO 

# Create a new client and connect to the server
client = MongoClient("mongodb://localhost:27017")


db = client['RecipeNama']
collection = db['recipes']

fs = GridFS(db)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def add_recipes(title,ingrediants,description, author,media_id):
    posted_at = datetime.utcnow().date().isoformat()
    recipe={ 
        'title' : title,
        'ingrediants' : ingrediants,
        'descriptions': description,
        'author' : author,
        'posted_at' : posted_at,
        'images' :  media_id
    }
    collection.insert_one(recipe)

def get_recipes():
    recipes = collection.find()
    return recipes

def get_recipe_this(id):
    query={'_id': ObjectId(id)}
    recipes = collection.find(query)
    return recipes

def author_recipes(username):
    query = {'author' : username}
    recipes = list(collection.find(query))
    return recipes

