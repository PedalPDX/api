# PedalAPI
# The following is the RESTFULL API for use by PedalPDX
# This code was aided in part the following article:
# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

from flask import Flask, jsonify, make_response, request
from random import randint
from os import listdir
from json import dump,load
from markdown import markdown

# The locations from which we will be handling flat files of JSON
# data containing the ride logs
rideLocations = "./rides/"

# Current Version
apiVersion = '0.4'

# The hostname of the server the api is hosted on
# TODO: Make this into a function that will grab this information
#       automatically.
apiHostname = '127.0.0.1'

# Port that the api will listen on.
apiPort = "5000"

# Pass the name of the app to flask
app = Flask(__name__)

# Define a simple function for returning useful information about the pedalAPI
# Converts the markdown README into html and serves to the requester
@app.route('/')
def index():
    with open("./README.md") as mark:
        return markdown(mark.read(), extensions=['tables'])

# Error Handler
# If the caller attempts to use a url not specified in the file, they will
# be given json information stating that there is no such page.
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({ 'error': 'Not found' }), 404)

# GET ------------------------------------------------------------

# Get request to return the current version of the API
@app.route('/version', methods = ['GET'])
def getVersion():
    return jsonify({'version': str(apiVersion)})

# Get all of the known rideID's
@app.route('/pedal/'+apiVersion+'/rides', methods = ['GET'])
def getAllRides():
    return jsonify({'RideIds': listdir(rideLocations)})

# Get the information on a single ride using an ID
@app.route('/pedal/'+apiVersion+'/rides/<string:id>', methods = ['GET'])
def getOneRide(id):
    return jsonify(getRideByID(id))

# Get the information about a ride by using the ID number
def getRideByID(id):
    with open(rideLocations+id) as ride:
        json_data = load(ride)
        return json_data

# POST -----------------------------------------------------------

# When posting to /rides, the entire json, including the ride ID are required
# The function will do moderate data checking to ensure all appropriate fields
# have been provided, and finally saves the data in the rideLocation directory
# under a filename denoted by the ride ID
@app.route('/pedal/'+apiVersion+'/rides', methods = ['POST'])
def addRide():
    if not request.json:
        return make_response(jsonify({ 'error': 'Requires JSON format'}), 400)
#    elif not 'version' in request.json:
#        return make_response(jsonify({ 'error': 'Requires pedalAPI version'}), 400)
#    elif request.json['version'] != apiVersion:
#        return make_response(jsonify({ 'error': 'Incorrect PedalAPI version'}), 400)
    elif not 'points' in request.json:
        return make_response(jsonify({ 'error': 'Requires location information'}), 400)
    elif not request.json['points']:
        return make_response(jsonify( { 'error': 'Requires location information' } ), 400)
    else:
        while True:
            num = genNumber()
            if num not in listdir(rideLocations):
                break
        ride = {
            'id': str(num),
            'version': apiVersion,
            'points': request.json['points']
        }
        with open(rideLocations+str(num), 'w') as dataFile:
            dump(ride, dataFile)
        return jsonify( { 'rideLink': apiHostname+':'+apiPort+'/pedal/'+apiVersion+'/rides/'+str(num) } ), 201

def genNumber():
    return randint(100000,999999)

# Main ------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug = True)
