import os
from flask import Flask, request, abort, jsonify, redirect
from flask import url_for, render_template
from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import *
from auth import AuthError, requires_auth
from datetime import datetime, date
import json
import logging
from six.moves.urllib.parse import urlencode


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    app.secret_key = os.environ['SECRET']

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Authorization, Content-Type')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, DELETE, PATCH')
        return response

    @app.route('/')
    def home():
        home_msg = 'Udacity Casting Agency'
        return jsonify(home_msg)

    """GET /movies
      Gets all movies in the database

      Returns:
          JSON Object -- json of all movies in the database
    """
    @app.route('/movies')
    @requires_auth('get:movies')
    def get_movies(payload):

        try:
            movies = Movie.query.order_by('id').all()
            movies_list = [Movie.format(movie) for movie in movies]
            result = {
              'success': True,
              'movies': movies_list
            }

        except:
            abort(422)

        return jsonify(result)

    """GET /actors
      Gets all actors in the database

      Returns:
          JSON Object -- json of all actors in the database
    """
    @app.route('/actors')
    @requires_auth('get:actors')
    def get_actors(payload):

        try:
            actors = Actor.query.order_by('id').all()
            actors = [actor.format() for actor in actors]

            result = ({
              'success': True,
              'actors': actors
            })

        except:
            abort(422)

        return jsonify(result)

    """POST /movies
      Creates and adds a new movie to the database

      Returns:
          JSON Object -- json of movie added if the entry is successful
    """
    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def new_movie(payload):

        # Get request json object
        body = request.get_json()
        title = body['title']
        release_date = datetime.strptime(body['release_date'],
                                         '%d-%m-%Y').date()
        actors = []

        # Try to insert the movie in the database

        try:

            if 'actors' in body:
                for id in body['actors']:
                    actor = Actor.query.filter(
                        Actor.id == id).one_or_none()

                    if actor:
                        actors.append(actor)

            movie_new = Movie(title=title,
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

    """POST /actors
      Creates and adds a new actor to the database

      Returns:
          JSON Object -- json of actor added if the entry is successful
    """
    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def new_actor(payload):

        # Get json request objects
        body = request.get_json()

        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        movies = []
        # Try to insert the actor in the database
        try:

            # If movie_id was included in the post find the movie
            if 'movies' in body:
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

    """'DELETE /movies/<int:movie_id>
        Deletes a movie from the database

      Inputs:
          int "movie_id"

      Returns:
          JSON Object -- json message if deletion is successful
    """
    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):

        # Delete movie with submitted id from database
        try:

            # Find movie with movie_id
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

            # if movie is none throw 404  
            if movie is None:
                abort(404)

            # Delete the movie
            movie.delete()

            result = {
                'success': True,
                'message': 'Deleted Movie ID: ' + str(movie_id)
            }

        except:
            abort(422)

        return jsonify(result)

    """'DELETE /actors/<int:actor_id>
      Deletes an actor from the database

      Inputs:
          int "actor_id"

      Returns:
          JSON Object -- json message if deletion is successful
    """
    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):

        # Delete actor with submitted id from database
        try:

            # Find actor with actor_id
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

            # If actor is none throw 404
            if actor is None:
                abort(404)

            # Delete the actor
            actor.delete()

            result = {
                'success': True,
                'message': 'Deleted Actor ID: ' + str(actor_id)
            }

        except:
            abort(422)

        return jsonify(result)

    """PATCH /movies/<int:movie_id>
      Edits a movie in the database

      Inputs:
          int "movie_id"

      Returns:
          JSON Object -- json message if edit is successful
    """
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def edit_movie(payload, movie_id):

        # Get the request info
        body = request.get_json()

        # Check that movie id exists
        movie = Movie.query.filter_by(id=movie_id).one_or_none()
        if movie is None:
            abort(404)

        # Check for updates to title and release date
        if 'title' in body:
            movie.title = body['title']
        if 'release_date' in body:
            movie.release_date = body['release_date']
        if 'actors' in body:
            for id in body['actors']:
                actor = Actor.query.filter(Actor.id == id).one_or_none()
                movie.actors.append(actor)

        # Modify the movie values and update
        movie.update()

        result = {
            "success": True,
            "movie": movie.format()
        }

        return jsonify(result)

    """PATCH /actors/<int:actor_id>
      Edits an actor in the database

      Inputs:
          int "actor_id"

      Returns:
          JSON Object -- json message if edit is successful
    """
    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def edit_actor(payload, actor_id):

        # Get the request info
        body = request.get_json()

        # Check that actor id exists
        actor = Actor.query.filter_by(id=actor_id).one_or_none()
        if actor is None:
            abort(404)

        # Check for updates to title and release date
        if 'name' in body:
            actor.name = body['name']
        if 'age' in body:
            actor.age = body['age']
        if 'gender' in body:
            actor.gender = body['gender']
        if 'movies' in body:
            for id in body['movies']:
                movie = Movie.query.filter(Movie.id == id).one_or_none()
                actor.movies_list.append(movie)

        # Modify the movie values and update
        actor.update()

        result = {
            "success": True,
            "actor": actor.format()
        }

        return jsonify(result)

    """
    Login Route

    The login route redirects to the Auth0 login page
    """
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
    app.run(host='0.0.0.0', port=8080)
