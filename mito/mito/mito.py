import os
import sys
import time
import signal
import logging
from flask import *
import sqlite3 as sql
from threading import Thread
from flask_socketio import SocketIO, disconnect
#import from local file
from my_database import *
#Debugging output is sent to debugLog.txt
logging.basicConfig(stream=sys.stderr,
					filemode='w+')
					filename='debugLog.txt',
					level=logging.DEBUG,
					format='%(asctime)-8s:	%(message)s',
					datefmt='%m/%d/%Y %H:%M:%S',
#debugging: set manually to true for debug printout in console
#DEV = False

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

#Initiate app
app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , mito.py
socketio = SocketIO(app, async_mode=async_mode)	#load socketio

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'mito.db'),
    SECRET_KEY='iLikeThisCourseALotRightNow2016-2017',
    USERNAME='admin',
    PASSWORD='1234'
))
app.config.from_envvar('MITO_SETTINGS', silent=True)

#set global variables
thread = None
doRun = True

#Initiate signalhandeler
def signal_handler(signal, frame):
	stopThread()
	sys.exit(0)

#Bind method for handleing ctrl+c
signal.signal(signal.SIGINT, signal_handler)
#-------------------------------------------------------
def connect_db():
    """Connects to the specific database."""
    rv = sql.connect(app.config['DATABASE'])
    return rv

def init_db():
	"""Initializes the database by rendering the code"""
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

#route initdb command here
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#Route ending of program through here
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#-------------------------------------------------------
#When a socket connects
@socketio.on('connect')
def connect():
    logging.info("new connection: " + request.sid)

#Recieve message from socket
#user['data'] = always current user
#request.sid = sessionID 
@socketio.on('msg')
def msg(user):
#	DEV
	logging.info("Client connected: " + user['data'])
	setSID(user['data'], request.sid, get_db())
	logging.info(printDB("users", get_db().cursor()))

#When a socket disconnects
@socketio.on('disconnect')
def disconnect():
	setTimeDc(request.sid, time.time(), get_db())
#	DEV
	logging.info("Client disconnected: " + request.sid)
	logging.info(printDB("users", get_db().cursor()))

#----------------------------------------------------
def timeout():
	"""
	Handles timing out sessions

	ARGS:
	------------
	NONE
	RETURNS:
	------------
	NONE
	"""
	#Within the same context
	with app.app_context():
		while doRun:
			#find time and get cursor
			timeNow = time.time()
			con = get_db().cursor()

#			DEV
			logging.info(printDB("users", get_db().cursor()))

			usList = con.execute("SELECT name FROM users").fetchall()
			#for-loop over all users
			for user in usList:
				#get time for user
				timeDc = getTimeDc(user, con)

#				DEV
				logging.info("User: %s and time %s", user, timeDc[0])

				#if user has a time set
				if timeDc[0]:
					if type(timeDc) is tuple:
						timeDc = timeDc[0]
					#If last activity was over 3 minutes ago, remove!
					if (timeNow - timeDc) > 180:
						removeDBEntries(user[0], get_db())
			#sleep for 4 seconds before starting again
			time.sleep(4)
def stopThread():
	"""
	Stops thread by changing global value of doRun

	ARGS:
	------------
	NONE
	RETURNS:
	------------
	NONE
	"""
	global doRun
	doRun = False

def isPair(user, partner):
	"""
	Checks if user and partner are in the same pair

	ARGS:
	------------
	user:string
		username
	partner:string
		username
	RETURNS:
	------------
	int:
		0: "partner not found"
		1: "is a pair"
		2: "paired with someone else"

	"""
#	DEV
	logging.info("User currently in isPair: %s", user)
	logging.info(printDB("users", get_db().cursor()))

	#Check for partner in database
	partner = getUser(partner, get_db().cursor())
	#If exists
	if partner:
		partner = partner[0]
		#get the pair-ID for user and partner
		u_pair=getPair(user, get_db().cursor())
		p_pair=getPair(partner, get_db().cursor())
		
#		DEV
		logging.info("p_pair: %s | u_pair: %s | u_pair != p_pair: %r", u_pair, p_pair, u_pair != p_pair)

		#Paired with someone else!
		if u_pair != p_pair:
			return 2

		#Should be a pair
		else: 
			#pair does not exist, create pair
			if not (u_pair and p_pair):
				#Create pairing and update database
				insertPair(user, partner, get_db())
				updateUsers(user, partner, get_db())
#				DEV
				logging.info("Inserted into database: user = %s and partner = %s", user, partner)
				logging.info(printDB("users", get_db().cursor()))
				logging.info(printDB("pairs", get_db().cursor()))

			#return 1
			return 1
	else:
		#Partner does not exist
		return 0

@app.route("/")
def renderBase(error=None):
	"""
	DESCR

	ARGS:
	------------
	error:string
		error-message
	RETURNS:
	------------
	HTML-template:
		basepage
	"""
	#Start thread for managing sessions
	global thread
	if thread is None: 
		thread = Thread(target=timeout)
		thread.start()

	return render_template('index.html', error=error)

@app.route("/loc", methods=['POST'])
def loc(error=None):
	"""
	Grabs new coordinates and re-renders map

	ARGS:
	------------
	error:string
		error-message
	RETURNS:
	------------
	HTML-template:
		meet:on success
		disconnect:on termination
		find_user:on error with location data
	"""
	assert request.method == 'POST'
	#Get input From form
	user = request.form["Username"]
	lon = request.form["lon"]
	lat = request.form["lat"]
	db = get_db()
	#Update location for user
	updateLoc(user, lon, lat, db)
	#Check for partner
	partner = getPartner(user, db.cursor())
	if partner == None:
		#ERROR!
		error="Pair no longer exists"
		deleteUser(user, db)
		#stop connection
		return render_template('/disconnect.html', error=error, redir=url_for('renderBase'))

	partner = partner[0]
	#Update midpoint
	updateMidpoint(user, partner, db)
	#get location data
	locLat1, locLon1 = getLocUser(user, db.cursor())
	locLat2, locLon2 = getLocUser(partner, db.cursor())
	#get midpoint
	midLon, midLat = getMidLoc(user, db)
	#If all values exist
	if (locLat1 and locLon1 and locLat2 and locLon2):
		#return
		return render_template('/meet.html', startLat=locLat1, startLon=locLon1, midLon=midLon, midLat=midLat, endLat=locLat2, endLon=locLon2, name=user)
		
	else:
		#ERROR!
		error="Location data error"
		return render_template('/find_user.html', error=error, name=user)

@app.route("/meet", methods=['POST'])
def meet(error=None):
	"""
	Finds new coordinates

	ARGS:
	------------
	error:string
		error-message
	RETURNS:
	------------
	HTML-template:
		loc
	"""
	assert request.method == 'POST'
	user = request.form["Username"]

	return render_template('/loc.html', name=user)

@app.route("/Find_User_form", methods=['POST'])
def Find_User_form(error=None):
	"""
	Finds new coordinates

	ARGS:
	------------
	error:string
		error-message
	RETURNS:
	------------
	HTML-template:
		find_user:on error
		meet:on succes
	"""
	#Make sure the method used is post.
	assert request.method == 'POST'
	#Get input from form
	partner = request.form["find_User"]
	user = request.form["Username"]

	#See if user and partner given is a pair already
	pair = isPair(user, partner)
	if pair == 1:
		#is a pair
		#get locs
		locLat1, locLon1 = getLocUser(user, get_db().cursor())
		locLat2, locLon2 = getLocUser(partner, get_db().cursor())
		#get midpoint
		midLon, midLat = getMidLoc(user, get_db())

#		DEV
		logging.info("Location data: Latitude user: %f Longitude user: %f", locLat1, locLon1)
		logging.info("Location data: Latitude partner: %f Longitude partner: %f", locLat2, locLon2)
		
		#if all location data is present
		if (locLat1 and locLon1 and locLat2 and locLon2):
			#return
			return render_template('/meet.html', startLat=locLat1, startLon=locLon1, midLon=midLon, midLat=midLat, endLat=locLat2, endLon=locLon2, name=user)
			
		else:
			#ERROR!
			error="Location data error"
			return render_template('/find_user.html', error=error, name=user)
	#Error - currently paired with someone else
	elif pair == 2:
		error="User currently paired with someone else"
		return render_template('/find_user.html', error=error, name=user)
	else:
		#User not found, return to last page
		error="User not found"
		return render_template('/find_user.html', error=error, name=user)

@app.route("/Store_User", methods=['POST'])
def Store_User(error=None):
	"""
	Args:
		Optional error-code
	Returns:
		Rendered template of same page, with error if user exists.
		Rendered template of 'search for new user'-page if not.
	"""
	"""
	Finds values from form and stores user

	ARGS:
	------------
	error:string
		error-message
	RETURNS:
	------------
	HTML-template:
		index:on error
		find_user:on success
	"""
	#Make sure the method used is post.
	assert request.method == 'POST'
	#Get input given
	user = request.form["Username"]
	lon = request.form["lon"]
	lat = request.form["lat"]

	#Look for user in database
	test = getUser(user, get_db().cursor())
	#if user already exists, redirect back with error
	if test:
		return render_template("/index.html", error="User already exists")
	#if not, insert in to database
	insertUser(user, lon, lat, get_db())
	#render
	return render_template('/find_user.html', name=user)

#For testing purposes
if __name__ == '__main__':
	"""
	Main method
	"""
	
	#start
	socketio.run(app, debug=True)