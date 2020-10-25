import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
from flask_migrate import Migrate

database_name = "myfridge"
database_path = "postgresql://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    migrate = Migrate(app, db)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


"""
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database

    Keyword arguments: n/a
    argument -- n/a
    Return: return_description
"""
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


'''
User-Product association table
'''
user_products = db.Table('user_products',     
      db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
      db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)

'''
User

'''
class User(db.Model):  
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True)
  first_name = Column(String)
  last_name = Column(String)
  age = Column(Integer)
  products = db.relationship('Product', backref='user', lazy=True)
  current_products = Column()
  past_products = Column()
  date_registered = Column(Integer)

  def __init__(self, question, weight, quantity, date_purchased):
    self.name = question
    self.weight = weight
    self.quantity = quantity
    self.date_purchased = date_purchased

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'weight': self.weight,
      'quantity': self.quantity,
      'date_purchased': self.date_purchased
    }

  def __repr__(self):
        return f'<User {self.id}: {self.last_name}, {self.first_name}>'


'''
Product

'''
class Product(db.Model):  
  __tablename__ = 'products'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  weight = Column(String)
  quantity = Column(String)
  date_purchased = Column(Integer)

  def __init__(self, name, weight, quantity, date_purchased, description=''):
    self.name = name
    self.description = description
    self.weight = weight
    self.quantity = quantity
    self.date_purchased = date_purchased

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'weight': self.weight,
      'quantity': self.quantity,
      'date_purchased': self.date_purchased
    }

  def __repr__(self):
        return f'<Product {self.id}: {self.last_name}, {self.first_name}>'

