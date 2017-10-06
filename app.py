from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from Database_setup import Base, Category,Items, User

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
engine = create_engine('sqlite:///ItemCatalogwithUser.db')
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

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


# creating new user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
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

#facebook login
@app.route('/fbconnect', methods=['POST'])
# check state token
def fbconnect():
    if request.args.get('state') != login_session['state']:
      response = make_response(json.dumps("Invalid state parameter"),404)
      response.headers['Content-Type'] = 'application/json'
      return response
    access_token = request.data
    print "access token recived %s" % access_token

# Exchange access token
    app_id = json.loads(open('fbclient_secrets.json', 'r').read())[
    'web']['app_id']
    app_secret = json.loads(
        open('fbclient_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' %(
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

# facebook Disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

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
    categories = session.query(Category).order_by(Category.name).all()
    if 'username' not in login_session:
        return render_template('publichomepage.html', categories = categories)
    else:
        return render_template('homepage.html', categories = categories)

#show all catagories
@app.route('/categories/new', methods = ['GET', 'POST'])
def Newcategory():
    if 'username'not in login_session:
        return redirect('/login') 
    if request.method == 'POST':
        newcategory = Category(name = request.form['name'], user_id=login_session['user_id'])

        session.add(newcategory)
        session.commit()
        flash('Category Successfully added %s' %newcategory.name)
        return redirect (url_for('Showcategories'))
    else:
        return render_template('newcategory.html')

#Edit Catagories
@app.route('/categories/<int:category_id>/edit', methods = ['GET' ,'POST'])
def Editcategory(category_id):
    editedcategory = session.query(Category).filter_by(id = category_id).one()

    if 'username'not in login_session:
        return redirect('/login') 
    if editedcategory.user_id != login_session['user_id']:
        return "<script> function myFunction(){ alert('you are not authorizd to Edit this Catalog. please create your own catalog item in order to edit it');}</script> <body onload = 'myFunction()'>"
    if request.method == 'POST':
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
    if 'username'not in login_session:
        return redirect('/login') 
    
    if DeleteToCategory.user_id != login_session['user_id']:
        return "<script> function myFunction(){ alert('you are not authorizd to Delete this Catalog. please create your own catalog item in order to Delete it');}</script> <body onload = 'myFunction()'>"
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
    creator = getUserInfo(category.user_id)
    items = session.query(Items).filter_by(category_id = category_id).all()
    
    if 'username' not in login_session:
        return render_template('publicitems.html', category = category , items = items)
    else:
        return render_template ('items.html', category = category , items = items, creator = creator)

@app.route('/categories/<int:category_id>/items/new', methods = ['GET','POST'])
def newitems(category_id):
    if 'username'not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id = category_id).one() 
    
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newitem = Items(name = request.form['name'], description = request.form['description'],img_url = request.form['img_url'] ,user_id = category.user_id,category_id = category_id)
        session.add(newitem)
        session.commit()
        flash ('Items Successfully added %s' % newitem.name)
        return redirect (url_for('Showitems', category_id = category_id))
    else:
        return render_template('newitem.html',category_id = category_id)

@app.route('/categories/<int:category_id>/<int:items_id>/edit' , methods = ['GET','POST'])
def edititem(category_id, items_id):
    if 'username'not in login_session:
        return redirect('/login') 
    category = session.query(Category).filter_by(id = category_id).one()
    editeditem = session.query(Items).filter_by(id = items_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script> function myFunction(){ alert('you are not authorizd to Edit this Catalog. please create your own catalog item in order to edit it');}</script> <body onload = 'myFunction()'>"
    if request.method == 'POST':
        if request.form ['name']:
            editeditem.name = request.form['name']
        if request.form ['description']:
            editeditem.description = request.form['description']
        if request.form ['img_url']:
            editeditem.img_url = request.form['img_url']
            session.add(editeditem)
            session.commit()
            flash ('Item Successfully edited %s' % editeditem.name)
            return redirect (url_for('Showitems', category_id = category_id))
    else:
        return render_template ('edititem.html',item = editeditem , category_id = category_id , items_id = items_id)

@app.route('/categories/<int:category_id>/<int:items_id>/delete' , methods = ['GET','POST'])
def deleteitem(category_id,items_id):
    if 'username'not in login_session:
        return redirect('/login') 
    category = session.query(Category).filter_by(id = category_id).one()
    deleteditem = session.query(Items).filter_by(id = items_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script> function myFunction(){ alert('you are not authorizd to Delete this Catalog. please create your own catalog item in order to delete it');}</script> <body onload = 'myFunction()'>"
    if request.method == 'POST':
    	
        session.delete(deleteditem)
        session.commit()
        flash ('Item Successfully deleted %s' %deleteditem.name)
        return redirect (url_for ('Showitems', category_id = category_id))
    else:
        return render_template ('deleteitem.html' , category_id = category_id , items_id = items_id , item = deleteditem )

# Disconnect 

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            login_session.clear()
            flash("You have successfully been logged out.")
            return redirect(url_for('Showcategories'))
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            login_session.clear()
        login_session.clear()
        flash("You have successfully been logged out.")
        return redirect(url_for('Showcategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('Showcategories'))

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)








