from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from Database_setup import Base, Category,Items

#New imports for google sign-in
from flask import session as login_session
import random , string

#connect to database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# API Endpoint
@app.route('/categories/JSON')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(categories =[r.serialize for r in categories] )

@app.route('/categories/<int:category_id>/items/<int:items_id>/JSON')
def ItemsJSON(category_id, items_id):
    items = session.query(Items).filter_by(id = items_id , category_id = category_id).one()
    return jsonify(items = items.serialize)

@app.route('/categories/<int:category_id>/items/JSON')
def category_itemsJSON(category_id):
    categories = session.query(Category).filter_by(id = category_id).one()
    category_items = session.query(Items).filter_by(category_id = category_id).all()
    return jsonify(items = [r.serialize for r in category_items])

if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)








