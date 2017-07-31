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

# show all categories
@app.route('/')
@app.route('/categories')
def Showcategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    return render_template('homepage.html', categories = categories)

@app.route('/categories/new', methods = ['GET', 'POST'])
def Newcategory():
    if request.method == 'POST':
        newcategory = Category(name = request.form['name'])
        session.add(newcategory)
        session.commit()
        flash('Category Successfully added %s' %newcategory.name)
        return redirect (url_for('Showcategories'))
    else:
        return render_template('newcategory.html')

@app.route('/categories/<int:category_id>/edit', methods = ['GET' ,'POST'])
def Editcategory(category_id):
    if request.method == 'POST':
    	editedcategory = session.query(Category).filter_by(id = category_id).one()

        if request.form ['name']:
            editedcategory.name = request.form['name']
            
            
            flash('Category Successfully Edited %s' %editedcategory.name)
            return redirect (url_for('Showcategories'))
        else:
            return render_template('editedcategory.html', category = editedcategory)

@app.route('/categories/<int:categories_id>/delete' , methods = ['GET','POST'])
def Deltecategory(category_id):
    if request.method == 'POST':
        deltecategory = session.query(Category).filter_by(id = category_id).one()
        session.delete(deltecategory)
        session.commit()
        flash ('Category Successfully deleted %s' %deltecategory.name)
        return redirect (url_for('Showcategories'))
    else:
        return render_template('deltecategory.html', category = deltecategory)

#show all items
@app.route('/categories/<int:category_id>/items' , methods = ['GET','POST'])
def Showitems(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Items).filter_by(category_id = category_id).all()
    return render_template ('items.html', category = category , items = items)

@app.route('/categories/<int:category_id>/items/new', methods = ['GET','POST'])
def newitems(category_id):
    if request.method == 'POST':
        newitem = Items(name = request.form['name'], description = request.form['description'], category_id = category_id)
        session.add(newitem)
        session.commit()
        flash ('Items Successfully added %s' % newitem.name)
        return redirect (url_for('Showitems', category_id = category_id))
    else:
        return render_template('newitem.html',category_id = category_id)

@app.route('/categories/<int:category_id>/<int:items_id>/edit' , methods = ['GET','POST'])
def edititem(category_id, items_id):
    if request.method == 'POST':
        category = session.query(Category).filter_by(id = category_id).one()
        editeditem = session.query(Items).filter_by(id = items_id).one()
        
    if request.form ['name']:
        editeditem.name = request.form['name']
    if request.form ['description']:
        editeditem.description = request.form['description']
        session.add(editeditem)
        session.commit()
        flash ('Item Successfully edited %s' % editeditem.name)
        return redirect (url_for('Showitems', category_id = category_id))
    else:
        return render_template ('edititem.html',item = editeditem , category_id = category_id , items_id = items_id)

@app.route('/categories/<int:category_id>/<int:items_id>/delete' , methods = ['GET','POST'])
def deleteitem(category_id,items_id):
    if request.method == 'POST':
    	category = session.query(Category).filter_by(id = category_id).one()
        deleteditem = session.query(Items).filter_by(id = items_id).one()
        session.delete(deleteditem)
        session.commit()
        flash ('Item Successfully deleted %s' %delteditem.name)
        return redirect (url_for ('Showitems', category_id = category_id))
    else:
        return render_template ('deleteitem.html' , category_id = category_id , items_id = items_id , item = deleteditem )












if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)








