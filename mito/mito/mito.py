import sqlite3 as sql
import os
import time
from my_database import *
from threading import Thread
from flask import *
from flask_socketio import SocketIO, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
#async_mode = None

thread = None

app = Flask(__name__)
socketio = SocketIO(app)#, async_mode=async_mode)	#load socketio
app.config.from_object(__name__) # load config from this file , mito.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'mito.db'),
    SECRET_KEY='iLikeThisCourseALotRightNow2016-2017',
    USERNAME='admin',
    PASSWORD='1234'
))
app.config.from_envvar('MITO_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sql.connect(app.config['DATABASE'])
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

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

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#-------------------------------------------------------
#TODO handle session
#@socketio.on('connect')
#def connect():
#	pass
#	 setTimeDc(user, None)
#	 DEV
#    print("new connection: " + request.sid)

#@socketio.on('disconnect')
#def disconnect():
#	pass
#    setTimeDc(time.time())
#	 DEV
#    print('Client disconnected: ' + request.sid)

#----------------------------------------------------
#TODO handle session
def timeout():
	pass
#	with app.app_context():
#		while True:
#			timeNow = time.time()
			#for all entries
			#forloop over users
#				timeDc = getTimeDc(user)
#				if timeDc:				
#					if (timeNow - timeDc) > 30:
#						removeDBEntries(user)
#			time.sleep(10)
#		DEV
#		print("dead " + curUser)


def isPair(user, partner):
	"""
	Takes two user-objects as arguments
	Creates a new pair if none of them are in a pair.
	Returns 2 if they are in a pair with someone else. Returns 1 if they are a pair. Returns 0 if error!
	"""
	partner = getUser(partner, get_db().cursor())

#	DEV
#	con.execute("SELECT * FROM users")
#	for x in con:
#		print(x)

	if partner:
		partner = partner[0]
		u_pair=getPair(user, get_db().cursor())
		p_pair=getPair(partner, get_db().cursor())
		
#		Dev
		print("Pairs")
		print(p_pair)
		print(u_pair)
		print(u_pair != p_pair)

		if u_pair != p_pair:
			#Paired with someone else!
			return 2
			
		else: 
			#pair does not exist, create pair
			if (not u_pair) and (not p_pair):
				#Create pairing
				insertPair(user, partner, get_db())

				updateUsers(user, partner, get_db())
#				DEV
				#con.execute("SELECT * FROM users")
#				for x in con:
#					print(x)
			#return 1 either way
			return 1
	else:
		#Partner does not exist
		return 0

@app.route("/")
def renderBase(error=None):
	"""
	Returns the rendered template of the base-page
	"""
	return render_template('index.html', error=error)

@app.route("/loc", methods=['POST'])
def loc(error=None):
	"""
	Gets new coordinates and re-renders
	Args:
		None
	Returns:
		Redirects back to the original page, after handling the input.
	Raises:
		None
	"""
	assert request.method == 'POST'
	#Get input given
	user = request.form["Username"]
	lon = request.form["lon"]
	lat = request.form["lat"]
	
	updateLoc(user, lon, lat, get_db())
	partner = getPartner(user, get_db().cursor())
	if partner == None:
		#ERROR!
		error="Pair no longer exists"
		deleteUser(user)
		return render_template('/disconnect.html', error=error)

	partner = partner[0]
	locLat1, locLon1 = getLocUser(user, get_db().cursor())
	locLat2, locLon2 = getLocUser(partner, get_db().cursor())
	if (locLat1 and locLon1 and locLat2 and locLon2):
		#return
		return render_template('/meet.html', startLat=locLat1, startLon=locLon1, endLat=locLat2, endLon=locLon2, name=user)
		
	else:
		#ERROR!
		error="Location data error"
		return render_template('/find_user.html', error=error, name=user)

@app.route("/meet", methods=['POST'])
def meet(error=None):
	assert request.method == 'POST'
	user = request.form["Username"]

	return render_template('/loc.html', name=user)

@app.route("/Find_User_form", methods=['POST'])
def Find_User_form(error=None):
	"""
	Takes an error-code as an optional argument

	Returns a rendered template of the same page, if there is an error.
	Returns a rendered template of the meet-up page if the user is found
	"""
	#Make sure the method used is post.
	assert request.method == 'POST'
	#Get input from form
	partner = request.form["find_User"]
	user = request.form["Username"]

	pair = isPair(user, partner)
	if pair == 1:
		#pair exists
		#get locs
		
		locLat1, locLon1 = getLocUser(user, get_db().cursor())
		locLat2, locLon2 = getLocUser(partner, get_db().cursor())
#		Dev
#		print(locLat1, locLon1, locLat2, locLon2)
		print("Users")
		print(user, partner)
		if (locLat1 and locLon1 and locLat2 and locLon2):
			#return
			global thread
			if thread is None:
				thread = Thread(target=timeout)
				thread.start()
			return render_template('/meet.html', startLat=locLat1, startLon=locLon1, endLat=locLat2, endLon=locLon2, name=user)
			
		else:
			#ERROR!
			error="Location data error"
			return render_template('/find_user.html', error=error, name=user)
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
	Extracts username from form. Stores username in a list.

	Args:
		Optional error-code
	Returns:
		Rendered template of same page, with error if user exists.
		Rendered template of 'search for new user'-page if not.
	"""
	#Make sure the method used is post.
	assert request.method == 'POST'
	#Get input given
	user = request.form["Username"]
	lon = request.form["lon"]
	lat = request.form["lat"]

	
	test = getUser(user, get_db().cursor())

	if test:
		return render_template("/index.html", error="User already exists")
		
	insertUser(user, lon, lat, get_db())
	#render
	return render_template('/find_user.html', name=user)


if __name__ == '__main__':
	"""
	Main method
	"""
	
	#start
	socketio.run(app, debug=True)