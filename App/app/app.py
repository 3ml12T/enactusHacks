
import os
import babel
import dateutil.parser
from flask import Flask, request, abort, jsonify, redirect
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



def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    #app.secret_key = os.environ['SECRET']
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\shahd\OneDrive\Desktop\MediDate Application\MediDate_Credentials\steel-aileron-266916-d88c69f449c7.json"

    #----------------------------------------------------------------------------#
    # Filters.
    #----------------------------------------------------------------------------#

    def format_datetime(value, format='medium'):
        date = dateutil.parser.parse(value)
        if format == 'full':
            format="EEEE MMMM, d, y 'at' h:mma"
        elif format == 'medium':
            format="EE MM, dd, y h:mma"
        return babel.dates.format_datetime(date, format)

    app.jinja_env.filters['datetime'] = format_datetime


    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Authorization, Content-Type')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, DELETE, PATCH')
        return response
    '''

    @app.route('/')
    def home():
        return render_template('pages/home.html')



    """GET /products
      Gets all products in the database

      Returns:
          JSON Object -- json of all products in the database
    """
    @app.route('/products')
    #@requires_auth('get:products')
    def get_products(payload):

        try:
            products = Product.query.order_by('id').all()
            products_list = [Product.format(product) for product in products]
            result = {
              'success': True,
              'products': products_list
            }

        except:
            abort(422)

        return jsonify(result)

    """GET /users
      Gets all users in the database

      Returns:
          JSON Object -- json of all users in the database
    """
    @app.route('/users')
    #@requires_auth('get:user')
    def get_users(payload):

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

    """POST /products
      Creates and adds a new movie to the database

      Returns:
          JSON Object -- json of movie added if the entry is successful
    """
    @app.route('/products', methods=['POST'])
    #@requires_auth('post:movies')
    def new_recipe(payload):

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

    """POST /users
      Creates and adds a new user to the database

      Returns:
          JSON Object -- json of user added if the entry is successful
    """
    @app.route('/users', methods=['POST'])
    #@requires_auth('post:user')
    def new_user(payload):

        # Get json request objects
        body = request.get_json()

        first_name = body.get('first_name', None)
        last_name = body.get('last_name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        movies = []
        # Try to insert the actor in the database
        try:

            # If movie_id was included in the post find the movie
            if 'users' in body:
                for movie_id in body['movies']:
                    movie = Movie.query.filter(
                        Movie.id == movie_id).one_or_none()

                if movie:
                    movies.append(movie)

            actor_new = Actor(name=name, age=age, gender=gender)
            actor_new.movies_list = [m for m in movies]
            actor_new.insert()

            result = {
              'success': True,
              'actor': actor_new.format()
            }

        except:
            abort(422)

        return jsonify(result)

    """'DELETE /products/<int:product_id>
        Deletes a product from the database

      Inputs:
          int "product_id"

      Returns:
          JSON Object -- json message if deletion is successful
    """
    @app.route('/products/<int:product_id>', methods=['DELETE'])
    #@requires_auth('delete:product')
    def delete_movie(payload, product_id):

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

    """PATCH /products/<int:product_id>
      Edits a recipe in the database

      Inputs:
          int "recipe_id"

      Returns:
          JSON Object -- json message if edit is successful
    """
    

    @app.route('/products/<int:product_id>', methods=['PATCH'])
    #@requires_auth('patch:product')
    def edit_product(payload, product_id):

        # Get the request info
        body = request.get_json()

        result = {
            "success": True,
            "recipe": 'FIXME!! Unimplemented'
        }

        return jsonify(result)
    

    """PATCH /users/<int:user_id>
      Edits an user in the database

      Inputs:
          int "user_id"

      Returns:
          JSON Object -- json message if edit is successful
    """
    @app.route('/users/<int:user_id>', methods=['PATCH'])
    #@requires_auth('patch:user')
    def edit_user(payload, user_id):

        # Get the request info
        body = request.get_json()

        # Check that actor id exists
        user = User.query.filter_by(id=user_id).one_or_none()
        if user is None:
            abort(404)

        # Check for updates to title and release date
        if 'first_name' in body:
            user.first_name = body['first_name']
        if 'last_name' in body:
            user.first_name = body['first_name']
        if 'age' in body:
            user.age = body['age']
        if 'products' in body:
            for id in body['products']:
                product = Product.query.filter(Product.id == id).one_or_none()
                user.products.append(product)

        # Modify the movie values and update
        user.update()

        result = {
            "success": True,
            "user": user.format()
        }

        return jsonify(result)


    '''
    def detect_text(path):
        """Detects text in the file."""
    # Imports the Google Cloud client library
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

    '''

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
