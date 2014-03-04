"""
PedalAPI

The following is the RESTFULL API for use by PedalPDX
"""

from flask import Flask, jsonify, make_response, request, redirect
from random import randint
from os import listdir
from json import dump, load
from markdown import markdown
import time
import Secrets
import psycopg2

# API root Directory
API_ROOT = "/var/www/api/"

# The locations from which we will be handling flat files of JSON
# data containing the ride logs
RIDELOCATIONS = API_ROOT + "/rides/"

# Log locations
LOG_DIR = API_ROOT + "/logs/"

# Current Version
APIVERSION = '0.4'

# The hostname of the server the API is hosted on
APIHOSTNAME = 'api.pedal.cs.pdx.edu'

# Port that the API will listen on.
APIPORT = 5001

# URLSTRING identifies the base for the API's URL
URLSTRING = 'http://' + APIHOSTNAME 

# Pass the name of the app to flask
app = Flask(__name__)


@app.route('/')
def index():
    """
    redirect toe the readme file for reference.
    """
    return redirect(URLSTRING + "/README.md", 302)


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
    is a human readable explanation of the issue. Also returns the cuurent time of
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
    return jsonify({'version': str(APIVERSION)})


@app.route('/rides', methods=['GET'])
def get_all_rides():
    """ Get all of the known ride IDs """
    return jsonify({'RideIds': listdir(RIDELOCATIONS)})


@app.route('/rides/<string:ride_id>', methods=['GET'])
def get_one_ride(ride_id):
    """ Get the information on a single ride using an ID """
    if ride_id not in listdir(RIDELOCATIONS):
        return error_gen(400, 200, "Ride Not Found")
    return jsonify(get_ride_by_id(ride_id))


def get_ride_by_id(ride_id):
    """ Get the information about a ride by using the ID number """
    with open(RIDELOCATIONS + ride_id) as ride:
        json_data = load(ride)
        return json_data

# POST -----------------------------------------------------------


@app.route('/rides', methods=['POST'])
def add_ride():
    """
    rideURL: 127.0.0.1:5000/rides/812241

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
            if num not in listdir(RIDELOCATIONS):
                break
        ride = {
            'id': str(num),
            'hash': request.json['hash'],
            'version': request.json['version'],
            'points': request.json['points']
        }
        with open(RIDELOCATIONS + str(num), 'w') as data_file:
            dump(ride, data_file)
        url_to_return = URLSTRING + '/rides/' + str(num)
        return make_response(jsonify({'RideURL': url_to_return}), 201)


def gen_number():
    """ Generate a random 6 digit number """
    return randint(100000, 999999)

def kml_maker(id, line_color, line_width, points):
    """
    kml_maker is in charge of making a kml string that can be returned through
    the API upon request
    """
    points_string = ""
    for (lng,lat) in points:
        s = lng + "," + lat + ',0'
        if not points_string:
            points_string = s
        else:
            points_string += '\n            ' + s
    kml ="""<?xml version="1.0" encoding="UTF-8"?>
  <kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
      <name>Pedal PDX trip {0}</name>
      <description>
       Distance: 5 Bagillion ft.\n
       AVG Spped: Ludacris speed\n
       Total time: 42 seconds\n
       Num Hotties passed: 6\n
       Donuts Burned: 22\n
       Num songs stuck in head: 3\n
      </description>
      <Style id="line">
        <LineStyle>
          <color>{1}</color>
          <width>{2}</width>
        </LineStyle>
        <PolyStyle>
          <color>7f00ff00</color>
        </PolyStyle>
      </Style>
      <Placemark>
        <name>Pedal PDX trip {0}</name>
        <description>
          Distance: 5 Bagillion ft.\n
          AVG Spped: Ludacris speed\n
          Total time: 42 seconds\n
          Num Hotties passed: 6\n
          Donuts Burned: 22\n
          Num songs stuck in head: 3\n
        </description>
        <styleUrl>#line</styleUrl>
        <LineString>
          <extrude>1</extrude>
          <tessellate>1</tessellate>
          <altitudeMode>absolute</altitudeMode>
          <coordinates>
            {3}
          </coordinates>
        </LineString>
      </Placemark>
    </Document>
  </kml>""".format(id, line_color, line_width, points_string)
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

    query = "SELECT ST_X(point), ST_Y(point) FROM points WHERE rideid = %s"
    args = filter(lambda x: x != "", [ride_id, accuracy, start_time, end_time])

    if accuracy:
                query += " AND accuracy < %s"
    if start_time:
                query += " AND time > %s"
    if end_time:
                query += " AND time < %s"

    # Create a psycopg2 cursor for the DB
    curr = conn.cursor()

    curr.execute(query, args)
    points = map(lambda (x,y): (str(x), str(y)), curr.fetchall())

    # End the cursor
    curr.close()
    # End the connection to the DB
    conn.close()
    return points

@app.route('/kml/<string:ride_id>', methods=['GET'])
def get_kml(ride_id):
    if ride_id not in listdir(RIDELOCATIONS):
                return error_gen(400, 200, "Ride Not Found")
    json_data = get_ride_by_id(ride_id)
    point_field = json_data['points']
    points = []
    for p in point_field:
                points.append((str(p['longitude']),str(p['latitude'])))
    kml_string = kml_maker(ride_id, "7fff0000", "9", points)
    response = make_response(kml_string)
    response.headers["Content-Type"] = "application/kml"
    return response



@app.route('/kml', methods=['POST'])
def get_kml_form():
        # Make sure the POST is correctly defined
    if not request.form:
                error_gen(400,400,"Must include form arguments")
    if not request.form["id"]:
                error_gen(400,410,"Must specify ride id")
    if not request.form["thickness"]:
                error_gen(400,411,"Must specify line thickness")
    if not request.form['accuracy']:
                error_gen(400,412,"Must specify accuracy threshold")
    if not request.form['start']:
                error_gen(400,413,"Must specify starting time")
    if not request.form['end']:
                error_gen(400,414,"Must specify ending time")
    if not request.form['color']:
                error_gen(400,415,"Must specify line color")

    # Accumulate the arguments
    color = request.form["color"]
    thick = request.form["thickness"]
    ride_id = request.form["id"]
    accuracy = request.form["accuracy"]
    start = request.form["start"]
    end = request.form["end"]

    points = query_db(ride_id, accuracy, start, end)

    kml_string = kml_maker(ride_id, color, thick, points)
    response = make_response(kml_string)
    response.headers["Content-Type"] = "application/kml"
    return response


@app.route('/map/<string:ride_id>', methods=['GET'])
def get_map(ride_id):
    return redirect('https://maps.google.com/maps?q=http://'+APIHOSTNAME+'/kml/'+ride_id,302)



# @app.route('/latest', methods=['GET'])
# def get_map(ride_id):
#     last = response.values.get("last")
#     return redirect('https://maps.google.com/maps?q=http://'+APIHOSTNAME+':5002/kml/'+ride_id,302)

# Main ------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True, port=APIPORT)
