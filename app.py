from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from Database_setup import Base, Category,Items

#New imports for google sign-in
from flask import session as login_session
import random , string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

#connect to database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id



    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = json.loads(answer.text)

    login_session['provider'] = 'provider'
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])

    print "done!"
    return output

# gdisconnect
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


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

#show all catagories
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

#Edit Catagories
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

#delete catagories
@app.route('/categories/<int:category_id>/delete' , methods = ['GET','POST'])
def Deletecategory(category_id):
    DeleteToCategory = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        
        session.delete(DeleteToCategory)
        
        flash ('Category Successfully deleted %s' %DeleteToCategory.name)
        session.commit()
        return redirect (url_for('Showcategories', category_id = category_id))
    else:
        return render_template('deletecategory.html', category = DeleteToCategory)

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
    category = session.query(Category).filter_by(id = category_id).one()
    editeditem = session.query(Items).filter_by(id = items_id).one()
    if request.method == 'POST':
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
    category = session.query(Category).filter_by(id = category_id).one()
    deleteditem = session.query(Items).filter_by(id = items_id).one()
    if request.method == 'POST':
    	
        session.delete(deleteditem)
        session.commit()
        flash ('Item Successfully deleted %s' %deleteditem.name)
        return redirect (url_for ('Showitems', category_id = category_id))
    else:
        return render_template ('deleteitem.html' , category_id = category_id , items_id = items_id , item = deleteditem )












if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)








