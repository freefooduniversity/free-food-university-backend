from ctypes.wintypes import FLOAT
import numbers
from app import db
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, validates

# declarative base class
Base = declarative_base()

class Marker(db.Model):
    __tablename__ = 'marker'
    id = Column(Integer, primary_key=True)
    food = Column(String(50))
    lat = Column(Float)
    long = Column(Float)
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