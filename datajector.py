#!/usr/bin/python

import psycopg2
import Secrets
import time
from os import listdir
from json import dump, load

# ----- CONFIG ----------

RUN_TIME = time.strftime("%c")

RIDES_DIRECTORY = "./rides/"

RIDES_TABLE = "rides"

LOG_FILE = "./logs/injector.log"

DEBUG = False
LOG_DEBUG = True

INSERT_TO_RIDES = "INSERT INTO rides VALUES (%s, %s, %s);"
INSERT_TO_POINTS = """INSERT INTO points
                   VALUES (%s, %s, %s, ST_PointFromText('Point(%s %s)', 4326));
                   """


# Debugging and Logging -------------------------------------------------------

def loggit(type, str):
    """ Log to the LogFile """
    with open(LOG_FILE, 'a') as log_file:
        log_file.write('[' + RUN_TIME + '] ' + type + ': ' + str + '\n')


# For debugging. If debugging is set, print the value
def debug(debug_string):
    if DEBUG:
        print(debug_string)
    if LOG_DEBUG:
        loggit('DEBUG', debug_string)

# Functions -------------------------------------------------------------------

def get_stored_ids():
    """ Get the list of rides currently stored in the DB """
    rides_in_db = []

    # Select the rows from a test DB
    curr.execute("SELECT * FROM rides;")

    # commit to start a new transaction
    conn.commit()

    # Fetch the list of tuples from the cursor
    database_results = curr.fetchall()
    debug("database_results: " + str(database_results))

    # Print each of the rows for debugging
    for row in database_results:
        debug("Row: " + str(row[0]))

    # Get the ride IDS from the results
    rides_in_db = map(lambda x: x[0], database_results)
    debug("rides_in_dB: " + str(rides_in_db))
    return rides_in_db


def get_rides_to_add(rides_in_db):
    """ Get the list of rides currently on disk """
    rides_to_add = []

    # Get the current list of rides, currently in the ridesDirectory
    rides_on_disk = listdir(RIDES_DIRECTORY)
    debug("rides_on_disk: " + str(rides_on_disk))

    # Identify the rides that need to be added into the DB
    rides_to_add = filter(lambda x: int(x) not in rides_in_db, rides_on_disk)
    debug("rides_to_add: " + str(rides_to_add))
    return rides_to_add


def add_ride(ride_id):
    """
    Given a rideid (filename) open the ride and store its data into the DB
    """
    # Open the file as data_file
    with open(RIDES_DIRECTORY + str(ride_id), 'r') as data_file:
        # Make an attempt to load the file's JSON information
        try:
            json_data = load(data_file)
        except:
            # If failure occurs, Log the error, and rollback the transaction
            loggit('MALFORMED_RIDE_ERROR',
                    'Could not successfully parse JSON in ride: ' + ride_id)
            conn.rollback()
            return -1
        # Ensure that the information contains an 'id' field
        if 'id' not in json_data:
            loggit('MALFORMED_RIDE_ERROR',
                    'Missing ride hash in ride: ' + ride_id)
            return -1
        # Ensure that the information contains a 'version' field
        if 'version' not in json_data:
            loggit('MALFORMED_RIDE_ERROR',
                    'Missing version in ride: ' + ride_id)
            return -1
        # Ensure that the information contains a 'points' array
        if 'points' not in json_data:
            loggit('MALFORMED_RIDE_ERROR',
                    'Missing points in ride: ' + ride_id)
            return -1
        # Get all of the required JSON information and store into variables
        ride_hash = json_data['id']
        ride_version = json_data['version']
        ride_points = json_data['points']
        try:
            # Make an attempt to add ride into the DB
            curr.execute(INSERT_TO_RIDES, (ride_id, ride_hash, ride_version))
        except:
            # If Failure occurs, log and rollback. Then return
            loggit('DB_ERROR',
                    'Error inserting ride information into db from ride: ' +
                    ride_id)
            conn.rollback()
            return -2
        # Iterate through the points, verify and add to the DB
        for point in ride_points:
            # Ensure 'accuracy' field is present
            if 'accuracy' not in point:
                loggit('MALFORMED POINT_ERROR',
                        'Missing accuracy for ride: ' + ride_id)
                return -1
            # Ensure 'time' field is present
            if 'time' not in point:
                loggit('MALFORMED POINT_ERROR',
                        'Missing time for ride: ' + ride_id)
                return -1
            # Ensure 'longitude' field is present
            if 'longitude' not in point:
                loggit('MALFORMED POINT_ERROR',
                        'Missing longitude for ride: ' + ride_id)
                return -1
            # Ensure 'latitude' field is present
            if 'latitude' not in point:
                loggit('MALFORMED POINT_ERROR',
                        'Missing latitude for ride: ' + ride_id)
                return -1
            # Collect the information into Variables
            point_acc = point['accuracy']
            point_time = point['time']
            point_long = point['longitude']
            point_lat = point['latitude']
            # Construct the postgis Geometry POINT
            point_geog = "POINT(" + str(point_lat) + ' ' + str(point_long) + ')'
            try:
                # Make an attempt to add the point to the DB
                curr.execute(
                    INSERT_TO_POINTS,
                    (ride_id, point_acc, point_time, point_lat, point_long))
            except:
                # If a point fails, log, rollback, and return
                loggit('DB_ERROR',
                       'Error inserting point into db from ride: '
                       + ride_id
                       + ' at time: '
                       + point_time)
                conn.rollback()
                return -3
        # If the file finishes, Commit the changes to the DB
        conn.commit()


if __name__ == '__main__':
    try:
        # Attempt to make a connection to the Database
        conn = psycopg2.connect(
                "dbname=" + Secrets.dbname +
                " user=" + Secrets.username +
                " host=" + Secrets.hostname +
                " password=" + Secrets.password)
    except:
        # On Failure, output a message saying so and retreat
        loggit('ERROR', "Unable to connect to the database")
        exit(-1)

    # Create a psycopg2 cursor for the DB
    curr = conn.cursor()
    # Get the list of rides from the DB
    in_db = get_stored_ids()
    # Determine which rides to add
    to_add = get_rides_to_add(in_db)
    # add the rides that need to be added
    for ride in to_add:
        add_ride(ride)

    # Ensure that any changes made to the DB Persist
    conn.commit()
    # End the cursor
    curr.close()
    # End the connection to the DB
    conn.close()
