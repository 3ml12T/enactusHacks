
import os
import babel
import dateutil.parser
from flask import Flask, request, abort, jsonify, redirect, flash
from flask import url_for, render_template
from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from .database.models import *
from .auth.auth import AuthError, requires_auth
from datetime import datetime, date
import json
import logging
from six.moves.urllib.parse import urlencode
from google.cloud import vision
import io
from .forms import *
import sys


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    #app.secret_key = os.environ['SECRET']
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\shahd\OneDrive\Desktop\MediDate Application\MediDate_Credentials\steel-aileron-266916-d88c69f449c7.json"
    UPLOAD_FOLDER = '/home/Jared/Desktop/Hackathon/enactusHacks/App/app/static/img/Receipts/'
    #----------------------------------------------------------------------------#
    # Functions.
    #----------------------------------------------------------------------------#

    def format_datetime(value, format='medium'):
        date = dateutil.parser.parse(value)
        if format == 'full':
            format="EEEE MMMM, d, y 'at' h:mma"
        elif format == 'medium':
            format="EE MM, dd, y h:mma"
        return babel.dates.format_datetime(date, format)

    app.jinja_env.filters['datetime'] = format_datetime



    def detect_text(path):
        """Detects text in the receipt file."""
    
        client = vision.ImageAnnotatorClient()

        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        d = {"Name": 0, "Fill Date": 0, "RX": 0, "Qty": 90, "date-to-take": 0, "Red": 0, "Blue": 0,"Green": 0}
        count = 0
        for text in texts:
            if(text.description == "Rx" or text.description == "Rx#" or text.description == "#" or text.description == "Rx:" or text.description == "Rx:#" or text.description == "Rx: #" or text.description == ":"):
                count = 1
                continue
            if(text.description[0:2] == "Qty"):
                d["Qty"] = text.description[3:len(text.description)-1]
                
            if(count == 1):
                d["RX"] = text.description
                count = 0
            vertices = (['({},{})'.format(vertex.x, vertex.y)
                        for vertex in text.bounding_poly.vertices])

            print('bounds: {}'.format(','.join(vertices)))
        return d

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
   
    #----------------------------------------------------------------------------#
    # Endpoints.
    #----------------------------------------------------------------------------#

    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Authorization, Content-Type')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, DELETE, PATCH')
        return response
    

    @app.route('/')
    def home():
        return render_template('pages/home.html')

    def upload_predict():
        if request.method == "POST":
            image_file = request.files["image"]
            if image_file:
                image_location = os.path.join(
                    UPLOAD_FOLDER,
                    image_file.filename
                )
                image_file.save(image_location)
                pred = detect_text
                return render_template("index.html", prediction=pred, image_name=image_file.filename)
    return render_template("index.html", prediction=0, image_name=None)


    """GET /products
      Gets all products in the database

      Returns:
          JSON Object -- json of all products in the database
    """
    @app.route('/products')
    #@requires_auth('get:products')
    def get_products():

        data= Product.query.distinct(Product.name, Product.weight).order_by(Product.name.asc()).all()
        
        return render_template('pages/products.html', products=data)

    """GET /users
      Gets all users in the database

      Returns:
          JSON Object -- json of all users in the database
    """
    @app.route('/users')
    #@requires_auth('get:user')
    def get_users():

        try:
            users = User.query.order_by('id').all()
            users = [user.format() for user in users]

            result = ({
              'success': True,
              'users': users
            })

        except:
            abort(422)

        return jsonify(result)

    """GET /products/create
      Creates and adds a new product to the database

      Returns:
          JSON Object -- json of movie added if the entry is successful
    """

    @app.route('/products/create', methods=['GET'])
    def create_product_form():
        form = ProductForm()   
        return render_template('forms/new_product.html', form=form)

    """POST /products
      Creates and adds a new product to the database

      Returns:
          JSON Object -- json of movie added if the entry is successful
    """
    @app.route('/products', methods=['POST'])
    #@requires_auth('post:product')
    def new_product():

        # Get request json object
        body = request.get_json()
        title = body['title']
        release_date = datetime.strptime(body['release_date'],
                                         '%d-%m-%Y').date()
        actors = []

        # Try to insert the movie in the database
        try:

            if 'products' in body:
                for id in body['products']:
                    product = Product.query.filter(
                        Product.id == id).one_or_none()

                    if product:
                        products.append(product)

            product_new = Product(title=title,
                              release_date=release_date,
                              actors=[])
            movie_new.actors = [a for a in actors]
            movie_new.insert()

            result = {
                'success': True,
                'movie': movie_new.title
            }

        except:
            abort(422)

        return jsonify(result)


    @app.route('/users/create', methods=['GET'])
    def create_user_form():
        form = UserForm()   
        return render_template('forms/new_user.html', form=form)

    """POST /users
      Creates and adds a new user to the database

      Returns:
          JSON Object -- json of user added if the entry is successful
    """
    @app.route('/users', methods=['POST'])
    #@requires_auth('post:user')
    def new_user():

        form = UserForm(request.form)
        print(form)
        error=False
        try:
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                age=form.age.data
            )
            db.session.add(user)
            db.session.commit()
            # on successful db insert, flash success
            flash('User ' + request.form['first_name'] + request.form['last_name'] + 
                ' was successfully listed!')
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist ' + User.first_name +
                User.last_name + ' could not be listed.')
        finally:
            db.session.close()
            
        return render_template('pages/home.html')

    """'DELETE /products/<int:product_id>
        Deletes a product from the database

      Inputs:
          int "product_id"

      Returns:
          JSON Object -- json message if deletion is successful
    """
    @app.route('/products/<int:product_id>', methods=['DELETE'])
    #@requires_auth('delete:product')
    def delete_product(product_id):

        # Delete product with submitted id from database
        try:
            # Find product with product_id
            product = Product.query.filter(Product.id == product_id).one_or_none()

            # if product is none throw 404  
            if product is None:
                abort(404)

            # Delete the product
            product.delete()

            result = {
                'success': True,
                'message': 'Deleted Product ID: ' + str(product_id)
            }

        except:
            abort(422)

        return jsonify(result)

    """'DELETE /users/<int:actor_id>
      Deletes an actor from the database

      Inputs:
          int "actor_id"

      Returns:
          JSON Object -- json message if deletion is successful
    """
    @app.route('/users/<int:user_id>', methods=['DELETE'])
    #@requires_auth('delete:user')
    def delete_user(payload, user_id):

        # Delete user with submitted id from database
        try:

            # Find user with user_id
            user = User.query.filter(User.id == user_id).one_or_none()

            # If actor is none throw 404
            if user is None:
                abort(404)

            # Delete the actor
            user.delete()

            result = {
                'success': True,
                'message': 'Deleted User ID: ' + str(user_id)
            }

        except:
            abort(422)

        return jsonify(result)


    """POST /products/<int:product_id>
      Edits a recipe in the database

      Inputs:
          int "recipe_id"

      Returns:
          JSON Object -- json message if edit is successful
    """
    @app.route('/products/<int:product_id>', methods=['POST'])
    #@requires_auth('patch:product')
    def edit_product(product_id):

        form = ProductForm()

        product_update=Product.query.filter_by(id=product_id).one_or_none()
        
        if product_update is None:
            abort(404)

        product={
            'id': product_update.id,
            'name' : product_update.name,
            'description' : product_update.description,
            'weight' : product_update.weight,
            'quantity' : product_update.date_purchased
        }

        form=ProductForm(data=product)
        
        return render_template('forms/edit_product.html', form=form, product=product)
    
    """GET /users/<int:user_id>/edit
      Edits an user in the database

      Inputs:
          int "user_id"

      Returns:
          JSON Object -- json message if edit is successful
    """
    @app.route('/users/<int:user_id>/edit', methods=['GET'])
    def edit_user(user_id):
        form = UserForm()
        user_update = User.query.filter_by(id=user_id).one_or_none()
        if user_update is None:
            abort(404)

        user={
            'id': user_update.id,
            'first_name' : user_update.first_name,
            'last_name' : user_update.last_name,
            'age' : user_update.age
        }

        form=UserForm(data=user)

        return render_template('forms/edit_artist.html', form=form, user=user)

    """POST /users/<int:user_id>/edit
      Edits an user in the database

      Inputs:
          int "user_id"

      Returns:
          JSON Object -- json message if edit is successful
    """
    @app.route('/users/<int:user_id>/edit', methods=['POST'])
    #@requires_auth('patch:user')
    def edit_user_submission(user_id):

        form = UserForm(request.form)
        try:
            user = User.query.filter_by(id=user_id).one()
            user.first_name=form.first_name.data
            user.last_name=form.last_name.data
            user.age=form.age.data

            db.session.commit()
            flash('User ' + request.form['first_name'] + 
                request.form['last_name'] + ' was updated successfully.')
        
        except:
            db.session.rollback()
            flash('An error occurred.  User ' + request.form['first_name'] + 
                request.form['last_name'] + ' failed to update.')

        return redirect(url_for('show_user', user_id=user_id))


    """
    Login Route

    The login route redirects to the Auth0 login page
    """
    '''
    @app.route('/login')
    def login():
        link = 'https://'
        link += os.environ['AUTH0_DOMAIN']
        link += '/authorize?'
        link += 'audience=' + os.environ['API_AUDIENCE'] + '&'
        link += 'response_type=token&'
        link += 'client_id=' + os.environ['CLIENT_ID'] + '&'
        link += 'redirect_uri=' + os.environ['CALLBACK_URL'] +\
            os.environ['CALLBACK_PATH']
        return redirect(link)

    """
    Logout Route

    The logout route logs out and redirects to the home page
    """
    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        link = 'https://'
        link += os.environ['AUTH0_DOMAIN']
        link += '/v2/logout?'
        link += 'client_id=' + os.environ['CLIENT_ID'] + '&'
        link += 'returnTo=' + os.environ['CALLBACK_URL']

        return redirect(link)
    '''
# ---------------------------------------------------------------------------#
# Errors.
# ---------------------------------------------------------------------------#

    # ERROR - BAD REQUEST (400)
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    # ERROR - UNAUTHORIZED (401)
    @app.errorhandler(401)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 401,
            'message': 'unauthorized'
        }), 401

    # ERROR - FORBIDDEN (403)
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 403,
            'message': 'forbidden'
        }), 403

    # ERROR - NOT FOUND (404)
    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    # ERROR - METHOD NOT ALLOWED (405)
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    # ERROR - UNPROCESSABLE (422)
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    # ERROR - INTERNAL SERVER ERROR (500)
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500
    
    # ERROR - AUTHENTICATION ERROR
    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error
        }), error.status_code
    
    return app

# ----------------------------------------------------------------------------#
# Ceate and Launch App.
# ----------------------------------------------------------------------------#

# Create App
app = create_app()


# Run App
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='127.0.0.1', port=8080)
