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
LOG_DEBUG = False


# Debugging ang Logging -------------------------------------------------------

def loggit(type, str):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write('[' + RUN_TIME + '] ' + type + ': ' + str + '\n')


# For debugging. If debugging is set, print the value
def debug(DEBUG_STRING):
    if DEBUG:
        print(debug_string)
    if LOG_DEBUG:
        loggit('DEBUG', debug_string)

# -----------------------------------------------------------------------------

# Begin Database communications
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

# -----------------------------------------------------------------------------


def get_stored_ids():
    rides_in_db = []
    # Select the rows from a test DB
    curr.execute("SELECT * FROM rides;")
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

in_db = get_stored_ids()

# -----------------------------------------------------------------------------


def get_rides_to_add(rides_in_db):
    rides_to_add = []

    # Get the current list of rides, currently in the ridesDirectory
    rides_on_disk = listdir(RIDES_DIRECTORY)
    debug("rides_on_disk: " + str(rides_on_disk))

    # Identify the rides that need to be added into the DB
    rides_to_add = filter(lambda x: int(x) not in rides_in_db, rides_on_disk)
    debug("rides_to_add: " + str(rides_to_add))
    return rides_to_add

to_add = get_rides_to_add(in_db)

# -----------------------------------------------------------------------------


def add_ride(ride_id):
    """
    Insert each of the files_to_add into the database
    """
    with open(RIDES_DIRECTORY + str(ride_id), 'r') as data_file:
        try:
            json_data = load(data_file)
        except:
            loggit('MALFORMED_RIDE_ERROR',
                    'Could not successfully parse JSON in ride: ' + ride_id)
            return -1
        if 'id' not in json_data:
            loggit('MALFORMED_RIDE_ERROR',
                    'Missing ride hash in ride: ' + ride_id)
            return -1
        if 'version' not in json_data:
            loggit('MALFORMED_RIDE_ERROR',
                    'Missing version in ride: ' + ride_id)
            return -1
        if 'points' not in json_data:
            loggit('MALFORMED_RIDE_ERROR',
                    'Missing points in ride: ' + ride_id)
            return -1
        ride_hash = json_data['id']
        ride_version = json_data['version']
        ride_points = json_data['points']
        conn.commit()
        try:
            debug("\"INSERT INTO rides (rideid, hash, version) VALUES (%(int)s, %(int)s, %(float)s);\",(" +
                    str(ride_id) + ", " +
                    str(ride_hash) + ", " +
                    str(ride_version) + ")")
        except:
            loggit('DB_ERROR',
                    'Error inerting ride information into db from ride: ' +
                    ride_id)
            return -2
        conn.commit()
        for point in ride_points:
            if 'accuracy' not in point:
                loggit('MALFORMED POINT_ERROR',
                        'Missing accuracy for ride: ' + ride_id)
                return -1
            if 'time' not in point:
                loggit('MALFORMED POINT_ERROR',
                        'Missing time for ride: ' + ride_id)
                return -1
            if 'longitude' not in point:
                loggit('MALFORMED POINT_ERROR',
                        'Missing longitude for ride: ' + ride_id)
                return -1
            if 'latitude' not in point:
                loggit('MALFORMED POINT_ERROR',
                        'Missing latitude for ride: ' + ride_id)
                return -1
            point_acc = point['accuracy']
            point_time = point['time']
            point_long = point['longitude']
            point_lat = point['latitude']
            try:
                debug("\"INSERT INTO points (rideid, accuracy, time, point) VALUES (%(int)s, %(float)s, %(timestamp)s, POINT(%s %s);\",(" +
                        str(ride_id) + ", " +
                        str(point_acc) + ", " +
                        str(point_time) + ", " +
                        str(point_long) + ", " +
                        str(point_lat) + ")")
            except:
                loggit('DB_ERROR',
                       'Error inerting point into db from ride: '
                       + ride_id
                       + ' at time: '
                       + point_time)
                return -3
            conn.commit()


# -----------------------------------------------------------------------------

for ride in to_add:
    add_ride(ride)

# Ensure that any changes made to the DB Persist
conn.commit()

#close the conection to the DB
curr.close()
conn.close()

# ----Accessory----------
