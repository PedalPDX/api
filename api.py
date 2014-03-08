#!/usr/bin/env python2
"""
PedalAPI

The following is the RESTFULL API for use by PedalPDX
"""

from flask import Flask, jsonify, make_response, request, redirect
from random import randint
from os import listdir
from json import dump, load
from markdown import markdown
from simplekml import Kml
import time
import Secrets
import psycopg2
import psycopg2.extras


# API root Directory
API_ROOT = "/var/www/api/"

# The locations from which we will be handling flat files of JSON
# data containing the ride logs
RIDE_LOCATIONS = API_ROOT + "/rides/"

# Log locations
LOG_DIR = API_ROOT + "/logs/"

# Current Version
API_VERSION = '0.4'

# The hostname of the server the API is hosted on
API_HOSTNAME = 'api.pedal.cs.pdx.edu'

# Port that the API will listen on.
API_PORT = 5001

# URL_STRING identifies the base for the API's URL
URL_STRING = 'http://' + API_HOSTNAME 

# Pass the name of the app to flask
app = Flask(__name__)


@app.route('/')
def index():
    """
    Redirect to the README file for reference.
    """
    return redirect(URL_STRING + "/README.md", 302)


@app.route('/README.md')
def readme():
    """
    Define a simple function for returning useful information about the
    PedalAPI Converts the markdown README into html and serves to the
    requester
    """
    with open(API_ROOT + "/README.md") as mark:
        return markdown(mark.read(), extensions=['tables'])


def error_gen(http_stat, error_code, error_desc):
    """
    Return a response to the requester with the given error. The HTTP code
    determines the http response code to send back. The Error code field is
    used to identify the particular issue that has been raised. The description
    is a human readable explanation of the issue. Also returns the current time of
    the server. All this information in also dumped to logs.
    """
    now = time.strftime("%c")
    response = {'error': str(error_desc), 
                'code': int(error_code),
		'time': now}
    with open(LOG_DIR+"error.log", "a") as log_file:
	dump(response, log_file)
        log_file.write("\n")
    return make_response(jsonify(response), http_stat)


@app.errorhandler(404)
def not_found(error):
    """
    If the caller attempts to use a URL not specified in the file, they will
    be given JSON information stating that there is no such page.
    """
    return error_gen(404, 100, "Requested page " + request.path + " does not exist")


@app.route('/VirtualEnvironment/run_locally.md')
def run_locally():
    """
    If the requestor clicks on the link to see the documentation for
    running the app in a virtual environment, retrieve the page and
    serve it, after having converted from markdown to HTML.
    """
    with open(API_ROOT + "/VirtualEnvironment/run_locally.md") as mark:
        return markdown(mark.read(), extensions=['tables'])

# GET ------------------------------------------------------------


@app.route('/version', methods=['GET'])
def get_version():
    """ Get request to return the current version of the API """
    return jsonify({'version': str(API_VERSION)})


@app.route('/rides', methods=['GET'])
def get_all_rides():
    """ Get all of the known ride IDs """
    return jsonify({'RideIds': listdir(RIDE_LOCATIONS)})


@app.route('/rides/<string:ride_id>', methods=['GET'])
def get_one_ride(ride_id):
    """ Get the information on a single ride using an ID """
    if ride_id not in listdir(RIDE_LOCATIONS):
        return error_gen(400, 200, "Ride Not Found")
    return jsonify(get_ride_by_id(ride_id))


def get_ride_by_id(ride_id):
    """ Get the information about a ride by using the ID number """
    with open(RIDE_LOCATIONS + ride_id) as ride:
        json_data = load(ride)
        return json_data

# POST -----------------------------------------------------------


@app.route('/rides', methods=['POST'])
def add_ride():
    """
    rideURL: 127.0.0.1/rides/812241

    The only POST function currently implemented is for posting rides to the
    server necessary arguments are the post version number, and a list of
    points in JSON. Currently, input should
    contain JSON like the following:
        {
        "points": [
            {
                "accuracy": 4.0,
                "latitude": 45.4,
                "longitude": -122.22,
                "time": "2013-1-12-3:21:32"
                },
            {
                "accuracy": 5.0,
                "latitude": 45.4,
                "longitude": -126.48,
                "time": "2013-1-12-3:25:32"
                }
            ],
        "version": 0.3
        "hash" : 12343234
        }

    Once the information has been posted, the user will receive JSON back.
    like so:
    {
        "RideURL": "api.pedal.cs.pdx.edu/rides/812241"
    }

    A URL in which the user may do a GET request in order to receive the
    information back from the server:

        {
        "id": "812241",
        "points": [
            {
                "accuracy": 4.0,
                "latitude": 45.4,
                "longitude": -122.22,
                "time": "210123"
                }
            ],
        "version": 0.3
        }

    """
    if not request.json:
        return error_gen(400, 300, "Requires JSON format")
    elif 'version' not in request.json:
        return error_gen(400, 310, "Missing 'version' field")
    elif 'hash' not in request.json:
        return error_gen(400, 311, "Missing 'hash' field")
    elif 'points' not in request.json:
        return error_gen(400, 312, "Missing 'points' field")
    elif not request.json['points']:
        return error_gen(400, 320, "Missing location information")
    else:
        while True:
            num = gen_number()
            if num not in listdir(RIDE_LOCATIONS):
                break
        ride = {
            'id': str(num),
            'hash': request.json['hash'],
            'version': request.json['version'],
            'points': request.json['points']
        }
        with open(RIDE_LOCATIONS + str(num), 'w') as data_file:
            dump(ride, data_file)
        url_to_return = URL_STRING + '/rides/' + str(num)
        return make_response(jsonify({'RideURL': url_to_return}), 201)


def gen_number():
    """ Generate a random 6 digit number """
    return randint(100000, 999999)


def kml_maker_2(ride_id, color, width, stats, points):
    icon_url = "http://www.clker.com/cliparts/r/J/F/7/y/4/placemark-hi.png"
    kml = Kml()
    if len(points) > 1:
        s = kml.newpoint(name='Start')
        s.coords = [points[0]]
        s.style.iconstyle.scale = 1
        s.style.iconstyle.icon.href = icon_url
        e = kml.newpoint(name='end')
        e.coords = [points[-1]]
        e.style.iconstyle.scale = 1
        e.style.iconstyle.icon.href = icon_url
    ls = kml.newlinestring(name = "Ride - " + ride_id)

    (rid, sp, ep, st, et, dur, dis) = stats[0]
    desc = "<![CDATA["
    desc += "<p>rideId   : " + str(rid) + "</p>"
    desc += "<p>Start    : " + str(sp) + "</p>"
    desc += "<p>End      : " + str(ep) + "</p>"
    desc += "<p>Began    : " + str(st) + "</p>"
    desc += "<p>Stopped  : " + str(et) + "</p>"
    desc += "<p>Duration : " + str(dur) + "</p>"
    desc += "<p>Distance : " + str(dis) + "</p>"
    desc += "]]>"
    ls.description = desc

    ls.coords = points
    ls.style.linestyle.width = 10
    ls.style.linestyle.color = "f7ff00ff"
    if color:
        ls.style.linestyle.color = color
    if width:
        ls.style.linestyle.width = width
    if 'start' in stats:
        ls.timespan.begin = stats['start']
    if 'end' in stats:
        ls.timespan.end = stats['end']
    return kml


def query_db(ride_id, accuracy, start_time, end_time):
    try:
        # Attempt to make a connection to the Database
        conn = psycopg2.connect(
             "dbname=" + Secrets.dbname +
             " user=" + Secrets.username +
             " host=" + Secrets.hostname +
             " password=" + Secrets.password)
    except:
        # On Failure, output a message saying so and retreat
        return ""

    statsq = "SELECT * FROM stats_view WHERE rideid = %s"
    query = "SELECT ST_X(point), ST_Y(point) FROM points WHERE rideid = %s"
    args = filter(lambda x: x != "", [ride_id, accuracy, start_time, end_time])

    if accuracy:
                query += " AND accuracy <= %s"
    if start_time:
                query += " AND time >= %s"
    if end_time:
                query += " AND time <= %s"

    # Create a psycopg2 cursor for the DB
    curr = conn.cursor()

    curr.execute(query, args)
    points = map(lambda (x,y): (str(x), str(y)), curr.fetchall())

    curr.execute(statsq, [ride_id])
    stats = curr.fetchall()

    # End the cursor
    curr.close()
    # End the connection to the DB
    conn.close()
    return (points, stats)


# @app.route('/kml/<string:ride_id>', methods=['GET'])
# def get_kml(ride_id):
#     if ride_id not in listdir(RIDE_LOCATIONS):
#                 return error_gen(400, 200, "Ride Not Found")
#     json_data = get_ride_by_id(ride_id)
#     point_field = json_data['points']
#     points = []
#     for p in point_field:
#                 points.append((str(p['longitude']),str(p['latitude'])))
#     kml_string = kml_maker_2(ride_id, "7fff0000", "9", {}, points)
#     response = make_response(kml_string.kml())
#     response.headers["Content-Type"] = "application/kml"
#     return response


@app.route('/kml/<string:ride_id>', methods=['GET'])
def new_kml(ride_id):
    acc = request.values.get("accuracy")
    if not acc:
	acc = "20"
    points, stats = query_db(ride_id, acc, "", "")
    kmel = kml_maker_2(ride_id, "", "", stats, points)
    response = make_response(kmel.kml())
    response.headers["Content-Type"] = "application/kml"
    return response


@app.route('/kml', methods=['POST'])
def get_kml_form():
        # Make sure the POST is correctly defined
    if not request.form:
                return error_gen(400,400,"Must include form arguments")
    if not request.form["id"]:
                return error_gen(400,410,"Must specify ride id")
    if not request.form["thickness"]:
                return error_gen(400,411,"Must specify line thickness")
    if not request.form['accuracy']:
                return error_gen(400,412,"Must specify accuracy threshold")
    if not request.form['start']:
                return error_gen(400,413,"Must specify starting time")
    if not request.form['end']:
                return error_gen(400,414,"Must specify ending time")
    if not request.form['color']:
                return error_gen(400,415,"Must specify line color")

    # Accumulate the arguments
    color = request.form["color"]
    thick = request.form["thickness"]
    ride_id = request.form["id"]
    accuracy = request.form["accuracy"]
    start = request.form["start"]
    end = request.form["end"]
    points, stats = query_db(ride_id, accuracy, start, end)
    kml_string = kml_maker_2(ride_id, color, thick, stats, points)
    response = make_response(kml_string.kml())
    response.headers["Content-Type"] = "application/kml"
    return response


@app.route('/clean/<string:ride_id>', methods=['GET'])
def get_cleaned(ride_id):
    acc = request.values.get("accuracy")
    if not acc:
	acc = "20"
    points, stats = query_db(ride_id, acc, "", "")
    kml_string = kml_maker_2(ride_id, "7f00ff00", "9", stats, points)
    response = make_response(kml_string.kml())
    response.headers["Content-Type"] = "application/kml"
    return response
     
@app.route('/map/<string:ride_id>', methods=['GET'])
def get_map(ride_id):
    return redirect('https://maps.google.com/maps?q=http://'+API_HOSTNAME+'/kml/'+ride_id,302)

 
@app.route('/latest', methods=['GET'])
def get_latest():
    try:
        # Attempt to make a connection to the Database
        conn = psycopg2.connect(
             "dbname=" + Secrets.dbname +
             " user=" + Secrets.username +
             " host=" + Secrets.hostname +
             " password=" + Secrets.password)
    except:
        # On Failure, output a message saying so and retreat
        return ""

    curr = conn.cursor()
    last = request.values.get("last")

    if last:
        query = "SELECT m.rideid, m.end FROM (Select rideid, max(time) AS end from points GROUP BY rideid) m ORDER BY m.end DESC LIMIT %s" 
        curr.execute(query, last)
    else:
        query = "SELECT m.rideid, m.end FROM (Select rideid, max(time) AS end from points GROUP BY rideid) m ORDER BY m.end DESC LIMIT 10;" 
        curr.execute(query)

    rides = map(lambda (x,y): (str(x), str(y)), curr.fetchall())
    result = {'latest': rides}
    return make_response(jsonify(result), 200)


    

# Main ------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True, port=API_PORT)
