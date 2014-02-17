"""
PedalAPI

The following is the RESTFULL API for use by PedalPDX
"""

from flask import Flask, jsonify, make_response, request
from random import randint
from os import listdir
from json import dump, load
from markdown import markdown

# The locations from which we will be handling flat files of JSON
# data containing the ride logs
RIDELOCATIONS = "./rides/"

# Current Version
APIVERSION = '0.4'

# The hostname of the server the api is hosted on
APIHOSTNAME = '127.0.0.1'

# Port that the api will listen on.
APIPORT = "5000"

<<<<<<< HEAD
# Pass the name of the APP to flask
=======
# URLSTRING identifies the base for the API's URL
URLSTRING = 'http://' + APIHOSTNAME + ':' + APIPORT

# Pass the name of the app to flask
>>>>>>> fb4627a... sqsh into style guid fix
APP = Flask(__name__)


@APP.route('/')
def index():
    """
    Define a simple function for returning useful information about the
    pedalAPI Converts the markdown README into html and serves to the
    requester
    """
    with open("./README.md") as mark:
        return markdown(mark.read(), extensions=['tables'])


@APP.errorhandler(404)
def not_found(error):
    """
    If the caller attempts to use a url not specified in the file, they will
    be given json information stating that there is no such page.
    """
    return make_response(jsonify({'error': 'Not found'}), 404)

# GET ------------------------------------------------------------


@APP.route('/version', methods=['GET'])
def get_version():
    """ Get request to return the current version of the API """
    return jsonify({'version': str(APIVERSION)})


@APP.route('/rides', methods=['GET'])
def get_all_rides():
    """ Get all of the known rideID's """
    return jsonify({'RideIds': listdir(RIDELOCATIONS)})


@APP.route('/rides/<string:rideid>', methods=['GET'])
def get_one_ride(ride_id):
    """ Get the information on a single ride using an ID """
    return jsonify(get_ride_by_id(ride_id))


def get_ride_by_id(ride_id):
    """ Get the information about a ride by using the ID number """
    with open(RIDELOCATIONS + ride_id) as ride:
        json_data = load(ride)
        return json_data

# POST -----------------------------------------------------------


@APP.route('/rides', methods=['POST'])
def add_ride():
    """
    deURL": "127.0.0.1:5000/rides/812241"The only POST function currently
    implemented is for posting rides to the server necessary arguuments are the
    post version number, and a list of points in JSON. Currently, input should
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
        }

    Once the information has been posted, the user will recieve JSON back.
    like so:
    {
        "RideURL": "127.0.0.1:5000/rides/812241"
    }

    A URL in which the user may do a GET request in order to recieve the
    information back from the server, which will be identical, plus the
    added id field, like so:
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
        return make_response(jsonify({'error': 'Requires JSON format'}), 400)
    elif not 'version' in request.json:
        return make_response(jsonify({'error': 'Requires version'}), 400)
    elif not 'points' in request.json:
        return make_response(jsonify(
            {'error': 'Requires location information'}), 400)
    elif not request.json['points']:
        return make_response(jsonify(
            {'error': 'Requires location information'}), 400)
    else:
        while True:
            num = gen_number()
            if num not in listdir(RIDELOCATIONS):
                break
        ride = {
            'id': str(num),
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

# Main ------------------------------------------------------------------------


if __name__ == '__main__':
    APP.run(debug=True)
