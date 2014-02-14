#!/usr/bin/python

import psycopg2
import Secrets
from os import listdir

# ----- CONFIG ----------

ridesDirectory = "./rides/"

ridesTable = "rides"

debugging = True

# -----------------------

# For debugging. If debugging is set, print the value
def debug(x,y):
	if debugging:
		print("Var " + x + ": " + str(y))

# Get the current list of rides, currently in the ridesDirectory
ridesOnDisk = listdir(ridesDirectory)
debug("ridesOnDisk", ridesOnDisk)



# Begin Database communications
try:
	# Attempt to make a connection to the Database
	conn = psycopg2.connect("dbname="+Secrets.dbname+" user="+Secrets.username+" host="+Secrets.hostname+" password="+Secrets.password)
except:
	# On Failure, output a message saying so and retreat
	print ("I am unable to connect to the database")
	exit(-1)

# Create a psycopg2 cursor for the DB
curr = conn.cursor()

# -----TESTING-----------

# Select the rows from a test DB
curr.execute("SELECT * FROM test;")

# Fetch the list of tuples from the cursor, and store into the results variable
databaseResults = curr.fetchall()

# Print each of the rows
for row in databaseResults:
	debug("Row",row[0])

# Get the ride IDS from the results
ridesInDB = map(lambda x: x[0], databaseResults)
debug("ridesInDB",ridesInDB)

# Identify the rides that need to be added into the DB
ridesToAdd = filter(lambda x: int(x) not in ridesInDB, ridesOnDisk)
debug("ridesToAdd",ridesToAdd)

# Print each of the rows
for ride in ridesToAdd:
	print("INSERT INTO "+ridesTable+" VALUES ("+ride+")")


# -----------------------

# Ensure that any changes made to the DB Persist
conn.commit()

#close the conection to the DB
curr.close()
conn.close()

# ----Accessory----------

