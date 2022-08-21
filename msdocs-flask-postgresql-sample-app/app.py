from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from random import randint
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
from models import Marker, Stats, Users, Phrases
db.create_all()
db.session.commit()


@app.route('/' + os.environ['free'] + '/', methods=['GET'])
def helloWorld():
    currentTime = convertStringToInt(datetime.now().strftime("%H : %M : %S"))
    return jsonify(currentTime)
'''
@app.route('/markers/all', methods=['GET'])
def getAllMarkers():
    markers = Marker.query.all()
    data = []
    for marker in markers:
        if (marker.end_time + marker.time_zone < convertStringToInt(datetime.now().strftime("%H:%M:%S")) or convertStringToInt(datetime.now().strftime("%H:%M:%S")) + 1200 < marker.end_time):
            deletePastMarkers(marker.id)
        else:
            data.append({'id': marker.id,
                    'food': marker.food,
                    'lat': marker.lat,
                    'long': marker.long,
                    'college': marker.college,
                    'capacity': marker.capacity,
                    'dibs': marker.dibs,
                    'likes': marker.likes,
                    'dislikes': marker.dislikes,
                    'creator_email': marker.creator_email,
                    'pic_url': marker.pic_url,
                    'start_time': marker.start_time,
                    'end_time': marker.end_time,
                    'time_zone': marker.time_zone,
                    'event':  marker.event,
                    'additional_info': marker.additional_info,
                    'building': marker.building})
    return jsonify(data)
'''


@app.route('/' + os.environ['free'] + '/stats/<string:college>', methods=['GET'])
def getUSAStats(college):
    stats = Stats.query.all()
    data = {}
    userCount = len(Users.query.all())
    seenCollege = False
    for stat in stats:
        if (stat.college == college):
            seenCollege = True
            data = {'id': stat.id,
                    'food_events': stat.food_events,
                    'fed_today': stat.fed_all_time,
                    'fed_all_time': userCount,
                    'college': stat.college}
    if not seenCollege:
        stat = Stats()
        stat.id = randint(0, 9999999)
        stat.food_events = 0
        stat.fed_today = 0
        stat.fed_all_time = 0
        stat.college = college
        db.session.add(stat)
        db.session.commit()
        data = {'id': stat.id,
                    'food_events': stat.food_events,
                    'fed_today': stat.fed_all_time,
                    'fed_all_time': userCount,
                    'college': stat.college}
    return jsonify(data)
    

@app.route('/' + os.environ['free'] + '/marker/add', methods=['POST'])
@csrf.exempt
def addMarker(): 
    marker = Marker()
    input = request.get_json()
    try:
        id = input['id']
        food = input['food']
        lat = input['lat']
        long = input['long']
        college = input['college']
        start_time = input['start_time']
        end_time = input['end_time']
        time_zone = input['time_zone']
        capacity = input['capacity']
        dibs = input['dibs']
        likes = input['likes']
        dislikes = input['dislikes']
        reports = input['reports']
        building = input['building']
        event = input['event']
        additional_info = input['additional_info']
        creator_email = input['creator_email']
        pic_url = input['pic_url']
    except(KeyError):
        return jsonify({"error":"error"})
    try:
        marker.id = id
        marker.food = food
        marker.lat = lat
        marker.long = long
        marker.college = college
        marker.start_time = start_time
        marker.end_time = end_time
        marker.time_zone = time_zone
        marker.capacity = capacity
        marker.dibs = dibs
        marker.likes = likes
        marker.dislikes = dislikes
        marker.reports = reports
        marker.creator_email = creator_email
        marker.building = building
        marker.event = event
        marker.additional_info = additional_info
        marker.pic_url = pic_url
    except(KeyError):
        return jsonify({"err":"err"})
    db.session.add(marker)
    db.session.commit()

# fed_today_changed == -1 for resetting fed_today and 1, 0 for no change, 1 for adding to it.
#fed_all_time is auto updated
@app.route('/' + os.environ['free'] + '/stats/fed_today/update/<string:college>', methods=['PATCH'])
@csrf.exempt
def updateFedToday(college): 
    stats = Stats()
    STATS = Stats.query.all()
    input = request.get_json()

    for stat in STATS:
        if stat.college == college:
            id = stat.id
            college = stat.college
            food_events = stat.food_events
            fed_today = stat.fed_today
            fed_all_time = stat.fed_all_time
            db.session.delete(stat)
            stat.id = id
            stat.college = college
            stat.food_events = food_events
            if input['fed_today_change'] == -1:
                stat.fed_today = 0
            else:
                stat.fed_today += input['fed_today_change']
            stat.fed_all_time += max(0, input['fed_today_change'])
            db.session.add(stat)
        if stat.college == 'all':
            id = stat.id
            college = stat.college
            food_events = stat.food_events
            fed_today = stat.fed_today
            fed_all_time = stat.fed_all_time
            db.session.delete(stat)
            stat.id = id
            stat.college = college
            stat.food_events = food_events
            if input['fed_today_change'] == -1:
                stat.fed_today = 0
            else:
                stat.fed_today += input['fed_today_change']
            stat.fed_all_time += max(0, input['fed_today_change'])
            db.session.add(stat)
    db.session.commit()


@app.route('/' + os.environ['free'] + '/stats/food_events/update/<string:college>', methods=['PATCH'])
@csrf.exempt
def updateFoodEvents(college): 
    stats = Stats()
    STATS = Stats.query.all()
    input = request.get_json()
    for stat in STATS:
        if stat.college == college:
            id = stat.id
            college = stat.college
            food_events = stat.food_events
            fed_today = stat.fed_today
            fed_all_time = stat.fed_all_time
            db.session.delete(stat)
            stat.id = id
            stat.college = college
            stat.food_events = input['food_events']
            stat.fed_today = fed_today
            stat.fed_all_time = fed_all_time
            db.session.add(stat)
    for stat in STATS:
        if stat.college == 'all' or stat.college == 'pickCollege':
            id = stat.id
            college = stat.college
            food_events = stat.food_events
            fed_today = stat.fed_today
            fed_all_time = stat.fed_all_time
            db.session.delete(stat)
            stat.id = id
            stat.college = college
            stat.food_events = input['food_events']
            stat.fed_today = fed_today
            stat.fed_all_time = fed_all_time
            db.session.add(stat)
    db.session.commit()

@app.route('/' + os.environ['free'] + '/marker/<string:college>', methods=["GET"])
@csrf.exempt
def getCollegeMarkers(college):
    colleges = []
    if (college == "all" or college == "pickCollege"):
        markers = Marker.query.all()
    else:
        markers = Marker.query.filter_by(college=college).all()
    for marker in markers:
         if (marker.end_time + marker.time_zone < convertStringToInt(datetime.now().strftime("%H:%M:%S")) or convertStringToInt(datetime.now().strftime("%H:%M:%S")) + 1200 < marker.end_time):
            deletePastMarkers(marker.id)
         else:
            colleges.append({'id': marker.id,
                    'food': marker.food,
                    'lat': marker.lat,
                    'long': marker.long,
                    'college': marker.college,
                    'capacity': marker.capacity,
                    'dibs': marker.dibs,
                    'likes': marker.likes,
                    'dislikes': marker.dislikes,
                    'creator_email': marker.creator_email,
                    'pic_url': marker.pic_url,
                    'start_time': marker.start_time,
                    'end_time': marker.end_time,
                    'reports': marker.reports,
                    'time_zone': marker.time_zone,
                    'event': marker.event,
                    'building': marker.building,
                    'additional_info': marker.additional_info})

    return jsonify(colleges)

def convertStringToInt(currentTime):
    newString = currentTime.split(":")
    newIntTime = int(newString[0]) * 100
    newIntTime += int(newString[1])
    
    return newIntTime


def deletePastMarkers(markerId):
    print("delete")
    deletedMarker = Marker.query.filter_by(id=markerId).first()
    db.session.delete(deletedMarker)
    db.session.commit()


# Returns list of colleges for all colleges provided for a given state
@app.route('/' + os.environ['free'] + '/marker/state', methods=['POST'])
@csrf.exempt
def getMarkersFromState(): 
    input = request.get_json()
    markers = Marker.query.all()
    data = []
    for marker in markers:
        if marker.college in input['colleges']:
            data.append({'id': marker.id,
                    'food': marker.food,
                    'lat': marker.lat,
                    'long': marker.long,
                    'college': marker.college,
                    'capacity': marker.capacity,
                    'dibs': marker.dibs,
                    'likes': marker.likes,
                    'dislikes': marker.dislikes,
                    'creator_email': marker.creator_email,
                    'pic_url': marker.pic_url,
                    'start_time': marker.start_time,
                    'end_time': marker.end_time,
                    'reports': marker.reports,
                    'time_zone': marker.time_zone,
                    'event': marker.event,
                    'building': marker.building,
                    'additional_info': marker.additional_info})
    return jsonify(data)

@app.route('/' + os.environ['free'] + '/stats/state', methods=['POST'])
@csrf.exempt
def getStatsForState():
    stats = Stats.query.all()
    input = request.get_json()
    id = randint(0, 9999999)
    food_events = 0
    fed_today = 0
    fed_all_time = 0
    for stat in stats:
        if stat.college in input['colleges']:
            food_events += stat.food_events
            fed_today += stat.fed_today
            fed_all_time += stat.fed_all_time
            
    data = {'id': id,
            'food_events': food_events,
            'fed_today': fed_today,
            'fed_all_time': fed_all_time,
            'college': "state"}
    return jsonify(data)

@app.route('/' + os.environ['free'] + '/marker/<string:college>/<string:food>', methods = ['GET'])
def getMarkersFromFoodAndCollege(college, food):
    markers = Marker.query.filter_by(college=college, food=food).all()
    markerArray = []
    for marker in markers:
        markerArray.append({'id': marker.id,
                        'food': marker.food,
                        'lat': marker.lat,
                        'long': marker.long,
                        'college': marker.college,
                        'capacity': marker.capacity,
                        'dibs': marker.dibs,
                        'likes': marker.likes,
                        'dislikes': marker.dislikes,
                        'reports': marker.reports,
                        'creator_email': marker.creator_email,
                        'pic_url': marker.pic_url,
                        'start_time': marker.start_time,
                        'end_time': marker.end_time,
                        'time_zone': marker.time_zone,
                        'event': marker.event,
                        'building': marker.building,
                        'additional_info': marker.additional_info})
    if (len(markerArray) > 0):
        return jsonify(markerArray)
    else: 
        return {}

# likes, dislikes, reports, sign ups, here
@app.route('/' + os.environ['free'] + '/marker/button/<string:id>/<string:button>/<string:college>', methods = ['GET'])
def patchMarker(id, button, college):
    All = Stats.query.filter_by(college="all").all()
    PickCollege = Stats.query.filter_by(college="pickCollege").all()
    College = Stats.query.filter_by(college=college).all()
    statAll = All[0]
    statPickCollege = PickCollege[0]
    statCollege = College[0]
    markersTemp = Marker.query.filter_by(id=id).all()
    marker = markersTemp[0]
    db.session.delete(markersTemp[0])
    db.session.delete(statPickCollege)
    db.session.delete(statAll)
    db.session.delete(statCollege)
    if (button == 'likes'):
        marker.likes += 1
        statAll.fed_today += 1
        statCollege.fed_today += 1
        statAll.fed_all_time += 1
        statCollege.fed_all_time += 1
        statPickCollege.fed_today += 1
        statPickCollege.fed_all_time += 1
    if (button == 'dislikes'):
        marker.dislikes += 1
    if (button == 'dibs'):
        marker.dibs += 1
        statAll.fed_today += 1
        statCollege.fed_today += 1
        statAll.fed_all_time += 1
        statCollege.fed_all_time += 1
        statPickCollege.fed_today += 1
        statPickCollege.fed_all_time += 1
    if (button == 'reports'):
        marker.reports += 1
    
    db.session.add(statPickCollege)
    db.session.add(statAll)
    db.session.add(statCollege)
    db.session.add(marker)
    db.session.commit()
    return jsonify(["success"])

@app.route('/' + os.environ['free'] + '/stats/fed_today/reset')
def resetFedToday():
    allStats = Stats.query.filter_by(college="all").all()
    if (allStats[0].fed_today == 0):
        return
    stats = Stats.query.all()
    for stat in stats:
        if not stat.fed_today == 0:
            db.session.delete(stat)
            stat.fed_today = 0
            db.session.add(stat)
    db.session.commit()

@app.route('/' + os.environ['free'] + '/marker/title/college/<string:food>/<string:building>/<string:college>')
def getMarkerByTitleAndCollege(food, building, college):
    markers = Marker.query.filter_by(food=food, building=building, college=college).all()
    Markers = []
    for marker in markers:
        Markers.append({'id': marker.id,
                        'food': marker.food,
                        'lat': marker.lat,
                        'long': marker.long,
                        'college': marker.college,
                        'capacity': marker.capacity,
                        'dibs': marker.dibs,
                        'likes': marker.likes,
                        'dislikes': marker.dislikes,
                        'reports': marker.reports,
                        'creator_email': marker.creator_email,
                        'pic_url': marker.pic_url,
                        'start_time': marker.start_time,
                        'end_time': marker.end_time,
                        'time_zone': marker.time_zone,
                        'event': marker.event,
                        'building': marker.building,
                        'additional_info': marker.additional_info})
    return jsonify(Markers)

@app.route('/' + os.environ['free'] + '/user/<string:email>', methods = ['GET'])
def getUserByEmail(email):
    users = Users.query.filter_by(email=email).all()
    userArr = []
    for user in users:
        userArr.append({'id': user.id,
                        'num_ppl_fed': user.num_ppl_fed,
                        'email': user.email,
                        'active_marker_id': user.active_marker_id,
                        'likes': user.likes,
                        'dislikes': user.dislikes,
                        'banned_status': user.banned_status})
    return jsonify(userArr)


@app.route('/' + os.environ['free'] + '/user/add', methods=['POST'])
@csrf.exempt
def addUser():
    user = Users()
    input = request.get_json()

    user.id= randint(1, 9999999),
    user.email= input['email'],
    user.num_ppl_fed= 0,
    user.likes= 0,
    user.dislikes= 0,
    user.banned_status= 0,
    user.active_marker_id =  0,

    checkUser = Users.query.filter_by(email=input['email']).all()
    if len(checkUser) == 0:
        db.session.add(user)
    db.session.commit()

@app.route('/' + os.environ['free'] + '/user/banned/<string:email>', methods=['GET'])
def banUser(email):
    users = Users.query.filter_by(email=email).all()
    for user in users:
        db.session.delete(user)
        user.banned_status = 1
        db.session.add(user)
    db.session.commit()

# action = 'likes' or 'dislikes'
@app.route('/' + os.environ['free'] + '/user/<string:action>/increment/<string:email>', methods=['GET'])
@csrf.exempt
def incrementProfile(action, email):
    users = Users().query.filter_by(email=email).all()

    for user in users:
        db.session.delete(user)
        if action == 'likes':
            user.likes += 1
        else:
            user.dislikes += 1
        user.num_ppl_fed += 1
        db.session.add(user)
    db.session.commit()

@app.route('/' + os.environ['free'] + '/marker/id/<string:id>', methods=["GET"])
@csrf.exempt
def getMarkerById(id):
    colleges = []
    markers = Marker.query.filter_by(id=id).all()
    for marker in markers:
            colleges.append({'id': marker.id,
                    'food': marker.food,
                    'lat': marker.lat,
                    'long': marker.long,
                    'college': marker.college,
                    'capacity': marker.capacity,
                    'dibs': marker.dibs,
                    'likes': marker.likes,
                    'dislikes': marker.dislikes,
                    'creator_email': marker.creator_email,
                    'pic_url': marker.pic_url,
                    'start_time': marker.start_time,
                    'end_time': marker.end_time,
                    'reports': marker.reports,
                    'time_zone': marker.time_zone,
                    'event': marker.event,
                    'building': marker.building,
                    'additional_info': marker.additional_info})

    return jsonify(colleges)

@app.route('/' + os.environ['free'] + '/user/marker/<string:action>/<string:email>/<string:id>', methods=['GET'])
def setUserMarkerId(action, email, id):
    users = Users.query.filter_by(email=email).all()
    for user in users:
        db.session.delete(user)
        if (action == 'set'):
            user.active_marker_id = id
        else:
            user.active_marker_id = 0
        db.session.add(user)
    db.session.commit()


@app.route('/' + os.environ['free'] + '/banned/phrases', methods=["GET"])
@csrf.exempt
def bannedPhrases():
    PHrases = []
    phrases = Phrases.query.all()
    for phrase in phrases:
            hash = 0
            for c in phrase.phrase:
                hash -= ord(c)
                hash += ord(c) % 7
                hash += (ord(c) + (ord(c) % len(phrase.phrase)))
                hash *= round((ord(c) * round(ord(c) / 2) / 4))
            PHrases.append({
                'phrase': hash % 10000000
            })

    return jsonify(PHrases)

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
