from ctypes.wintypes import FLOAT
import numbers
from xmlrpc.client import Boolean
try:
    from app import db
except ImportError:
    from __main__ import db
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, validates

# declarative base class
Base = declarative_base()

class Marker(db.Model):
    __tablename__ = 'marker'
    id = Column(Integer, primary_key=True)
    food = Column(String(20))
    lat = Column(Float)
    long = Column(Float)
    college = Column(String(20))
    start_time = Column(String(10))
    end_time = Column(String(10))
    time_zone = Column(Integer)
    capacity = Column(Integer)
    dibs = Column(Integer)
    likes = Column(Integer)
    dislikes = Column(Integer)
    reports = Column(Integer)
    building = Column(String(50))
    event = Column(String(100))
    additional_info = Column(String(300))
    creator_email = Column(String(50))
    pic_url = Column(String(500)) # url from firebase image service 
    def __str__(self):
        return self.food

class Stats(db.Model):
    __tablename__ = 'stats'
    id = Column(Integer, primary_key=True)
    food_events = Column(Integer)
    fed_today = Column(Integer)
    fed_all_time = Column(Integer)
    college = Column(String(50))
    def __str__(self):
        return self.food_events

class Users(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(50))
    num_ppl_fed = Column(Integer)
    likes = Column(Integer)
    dislikes = Column(Integer)
    active_marker_id = Column(Integer)
    banned_status = Column(Integer)
    
'''
class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))
    def __str__(self):
        return self.name

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates('rating')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return self.restaurant.name + " (" + self.review_date.strftime("%x") +")"
        '''