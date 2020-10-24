from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import Actor, Movie, setup_db
from app import create_app, app
from models import db
import unittest
import os
import json
import datetime

# database_path = os.environ['DATABASE_TEST_URL']
database_path = os.environ['DATABASE_URL']

# Get Environment Variable Tokens
ca_token = os.environ['CA_TOKEN']  # Casting Assistant
cd_token = os.environ['CD_TOKEN']  # Casting Director
ep_token = os.environ['EP_TOKEN']  # Executive Producer

# ----------------------------------------------------------------------------
# Test Cases
# ----------------------------------------------------------------------------


class MainTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app, database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

        self.new_movie = {
            'title': 'Napoleon Dynamite',
            'release_date': '5-5-2009',
            'actors': [10, 11]
        }

        self.new_actor = {
            'name': 'Drew Barrymore',
            'age': '46',
            'gender': 'F',
            'movies': [1]
        }

    def tearDown(self):
        """Executed after reach test"""
        pass
#
# GET REQUESTS ---------------------------------------------------------------
#
    # GET Movies test - success

    def test_get_movies(self):
        res = self.client().get('/movies', headers={
            'Authorization': 'Bearer ' + str(ca_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    # GET Movies test - failure - endpoint not found
    def test_404_not_found_get_movies(self):
        res = self.client().get('/movy', headers={
            "Authorization": 'Bearer ' + str(ca_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)

    # GET Actors test - success
    def test_get_actors(self):
        res = self.client().get('/actors', headers={
            "Authorization": 'Bearer ' + str(ca_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    # GET Actors test - failure - endpoint not found
    def test_404_not_found_get_actors(self):
        res = self.client().get('/actrs', headers={
            "Authorization": 'Bearer ' + str(ca_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)

#
# POST REQUESTS ---------------------------------------------------------------
#
    # POST Movie test - success
    def test_new_movie(self):
        res = self.client().post(
            '/movies',
            json={
                "title": "The Big Short",
                "release_date": "5-5-2014",
                "actors": [4, 1]},
            headers={'Authorization': 'Bearer ' + str(ep_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    # POST Movie test - failure - unprocessible request
    def test_422_unprocessible_new_movie(self):
        res = self.client().post(
            '/movies',
            json={
                "title": "The Big Short",
                "release_date": "5-5-2014",
                "actors": ["as"]},
            headers={"Authorization": 'Bearer ' + str(ep_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)

    # POST Movie test - failure - not found request
    def test_404_not_found_new_movie(self):
        res = self.client().post(
            '/movis',
            json={
                "title": "The Big Short",
                "release_date": "5-5-2014",
                "actors": [6, 7]},
            headers={"Authorization": 'Bearer ' + str(ep_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)

    # POST Movie test - failure - unauthorized permission
    def test_401_unauthorized_new_movie(self):
        res = self.client().post(
            '/movies',
            json={
                "title": "The Big Short",
                "release_date": "5-5-2014",
                "actors": [2]},
            headers={"Authorization": 'Bearer ' + str(ca_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

    # POST Actor test - success
    def test_new_actor(self):
        res = self.client().post(
            '/actors',
            json={
                "name": "Drew Barrymore",
                "age": "46",
                "gender": "F",
                "movies": [2]},
            headers={"Authorization": 'Bearer ' + str(cd_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    # POST Actor test - failure - unprocessible
    def test_422_unprocessible_new_actor(self):
        res = self.client().post(
            '/actors',
            json={
                "name": "Drew Barrymore",
                "age": "46",
                "gender": "F",
                "movies": ["drew"]},
            headers={"Authorization": 'Bearer ' + str(cd_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)

    # POST Actor test - failure - unauthorized
    def test_401_unauthorized_new_actor(self):
        res = self.client().post(
            '/actors',
            json={
                "name": "Drew Barrymore",
                "age": "46",
                "gender": "F",
                "movies": [1]},
            headers={"Authorization": 'Bearer ' + str(ca_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)
#
# PATCH REQUESTS --------------------------------------------------------------
#
    # PATCH Movie test - success

    def test_edit_movie(self):
        res = self.client().patch(
            '/movies/2',
            json={
                "title": "Superbad",
                "release_date": "8-9-2010",
                "actors": [1]},
            headers={"Authorization": 'Bearer ' + str(ep_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    # PATCH Movie test - failure - not found
    def test_404_not_found_edit_movie(self):
        res = self.client().patch(
            '/movies/2500',
            json={
                "title": "Superbad",
                "release_date": "8-9-2010",
                "actors": [1]},
            headers={"Authorization": 'Bearer ' + str(ep_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)

    # PATCH Movie test - failure - unauthorized request
    def test_401_unauthorized_edit_movie(self):
        res = self.client().patch(
            '/movies/2',
            json={
                "title": "Superbad",
                "release_date": "8-9-2010",
                "actors": [1]},
            headers={'Authorization': 'Bearer ' + str(ca_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

    # PATCH Actor test - success
    def test_edit_actor(self):
        res = self.client().patch(
            '/actors/1',
            json={
                "name": "Billy Crystal",
                "age": "60",
                "gender": "M",
                "movies": [2]},
            headers={"Authorization": 'Bearer ' + str(ep_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    # PATCH Actor test - failure - not found
    def test_404_not_found_edit_actor(self):
        res = self.client().patch(
            '/actors/400',
            json={
                "name": "Billy Crystal",
                "age": "60",
                "gender": "M",
                "movies": [2]},
            headers={"Authorization": 'Bearer ' + str(ep_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)

    # PATCH Actor test - failure - unauthorized request
    def test_401_unauthorized_edit_actor(self):
        res = self.client().patch(
            '/actors/2300',
            json={
                "name": "Billy Crystal",
                "age": "60",
                "gender": "M",
                "movies": [2]},
            headers={"Authorization": 'Bearer ' + str(ca_token)}
            )
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)
#
# DELETE REQUESTS -------------------------------------------------------------
#

    # DELETE Movie test - success
    def test_delete_movie(self):
        new_movie = Movie(title=self.new_movie['title'],
                          release_date=self.new_movie['release_date'],
                          actors=[])
        new_movie.insert()

        for a in self.new_movie['actors']:
            print(new_movie.actors)
            b = Actor.query.filter(Actor.id == a).one_or_none()
            if b:
                new_movie.actors.append(b)

        new_movie.update()
        print(new_movie.actors)
        prev_num_of_movies = len(Movie.query.all())

        # Delete question and load data
        res = self.client().delete((f'/movies/{new_movie.id}'), headers={
            "Authorization": 'Bearer ' + str(ep_token)})
        body = json.loads(res.data)
        num_of_movies = len(Movie.query.all())
        movie = Movie.query.filter(Movie.id == new_movie.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertEqual(movie, None)
        self.assertTrue(prev_num_of_movies - num_of_movies == 1)

    # DELETE Movie test - failure - unprocessible request
    def test_422_unprocessible_delete_movie(self):
        res = self.client().delete('/movies/1000', headers={
            "Authorization": 'Bearer ' + str(ep_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)

    # DELETE Movie test - failure - unauthorized request
    def test_401_unauthorized_delete_movie(self):
        res = self.client().delete('/movies/2', headers={
            "Authorization": 'Bearer ' + str(ca_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

    # DELETE Actor test - success
    def test_delete_actor(self):
        new_actor = Actor(name=self.new_actor['name'],
                          age=self.new_actor['age'],
                          gender=self.new_actor['gender'])

        new_actor.insert()

        for a in self.new_actor['movies']:
            print(new_actor.movies_list)
            b = Movie.query.filter(Movie.id == a).one_or_none()
            if b:
                new_actor.movies_list.append(b)

        new_actor.update()
        print(new_actor.movies_list)
        prev_num_of_actors = len(Actor.query.all())

        res = self.client().delete(f'/actors/{new_actor.id}', headers={
            "Authorization": 'Bearer ' + str(ep_token)})
        body = json.loads(res.data)
        num_of_actors = len(Actor.query.all())
        actor = Actor.query.filter_by(id=new_actor.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertEqual(actor, None)
        self.assertTrue(prev_num_of_actors - num_of_actors == 1)

    # DELETE Actor test - failure - unprocessible request
    def test_422_unprocessible_delete_actor(self):
        res = self.client().delete('/actors/5000', headers={
            "Authorization": 'Bearer ' + str(ep_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)

    # DELETE Actor test - failure - unprocessible request
    def test_404_not_found_delete_actor(self):
        res = self.client().delete('/actor/555', headers={
            "Authorization": 'Bearer ' + str(ep_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)

    # DELETE Actor test - failure - unauthorized request
    def test_401_unauthorized_delete_actor(self):
        res = self.client().delete('/actors/2', headers={
            "Authorization": 'Bearer ' + str(ca_token)})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

#
# VARIOUS REQUESTS ------------------------------------------------------------
#
    # GET Movies without header - unauthorized request
    def test_401_unauthorized_no_header_get_movies(self):
        res = self.client().get('/movies')
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

# ----------------------------------------------------------------------------
# Launch unittest
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
