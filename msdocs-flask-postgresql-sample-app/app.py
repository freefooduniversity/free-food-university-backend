from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if not 'WEBSITE_HOSTNAME' in os.environ:
   # local development, where we'll use environment variables
   print("Loading config.development and environment variables from .env file.")
   app.config.from_object('azureproject.development')
else:
   # production
   print("Loading config.production.")
   app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# Create databases, if databases exists doesn't issue create
# For schema changes, run "flask db migrate"
from models import Marker, Stats
db.create_all()
db.session.commit()

@app.route('/', methods=['GET'])
def helloWorld():
    return jsonify({"message": "Free Food University API. You're in the right place."})

@app.route('/marker/all', methods=['GET'])
def getAllMarkers():
    markers = Marker.query.all()
    data = []
    for marker in markers:
        data.append({'id': marker.id,
                'food': marker.food,
                'lat': marker.lat,
                'long': marker.long})
    return jsonify(data)

@app.route('/stats/<string:college>', methods=['GET'])
def getUSAStats(college):
    stats = Stats.query.all()
    data = {}
    for stat in stats:
        if (stat.college == college):
            data = {'id': stat.id,
                    'food_events': stat.food_events,
                    'fed_today': stat.fed_today,
                    'fed_all_time': stat.fed_all_time,
                    'college': stat.college}
    return jsonify(data)
    

@app.route('/marker/add', methods=['POST'])
@csrf.exempt
def addMarker(): 
    marker = Marker()
    input = request.get_json()
    try:
        id = input['id']
        food = input['food']
        lat = input['lat']
        long = input['long']
    except(KeyError):
        return jsonify({"error":"error"})
    try:
        marker.id = id
        marker.food = food
        marker.lat = lat
        marker.long = long
    except(KeyError):
        return jsonify({"err":"err"})
    db.session.add(marker)
    db.session.commit()

@app.route('/stats/update/<string:college>', methods=['PATCH'])
@csrf.exempt
def updateStats(college): 
    food_events = stat.food_events
    fed_today = stat.fed_today
    fed_all_time = stat.fed_all_time
    method = request.form.get('method')
    statChanging = request.form.get('statChanging')
    stats = Stats.query.all()
    for stat in stats:
        if (stat.college == college):
            if (statChanging == 'food_events'):
                if (method == 'add'):
                    food_events += 1
                else: 
                    food_events -= 1
            else:
                if (method == 'add'):
                    fed_today += 1
                    fed_all_time += 1
                else:
                    fed_today = 0

    stat.food_events = food_events
    stat.fed_today = fed_today
    stat.fed_all_time = fed_all_time

    db.session.add(stat)
    db.session.commit()

'''
@app.route('/<int:id>', methods=['GET'])
def details(id):
    from models import Restaurant, Review
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant==id)
    return jsonify({"restaurant id: ": restaurant.id,
                    "name: ": restaurant.name})
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    from models import Restaurant
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
    except (KeyError):
        # Redisplay the question voting form.
        return render_template('add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        db.session.add(restaurant)
        db.session.commit()

        return redirect(url_for('details', id=restaurant.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    from models import Review
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        review_text = request.values.get('review_text')
    except (KeyError):
        #Redisplay the question voting form.
        return render_template('add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        review = Review()
        review.restaurant = id
        review.review_date = datetime.now()
        review.user_name = user_name
        review.rating = int(rating)
        review.review_text = review_text
        db.session.add(review)
        db.session.commit()
                
    return redirect(url_for('details', id=id))        

@app.context_processor
def utility_processor():
    def star_rating(id):
        from models import Review
        reviews = Review.query.where(Review.restaurant==id)

        ratings = []
        review_count = 0;        
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = sum(ratings)/len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
'''
if __name__ == '__main__':
   app.run()
