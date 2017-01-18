import sqlite3 as sql
import os
import time
from threading import Thread
from flask import *
from flask_socketio import SocketIO, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

thread = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)	#load socketio
app.config.from_object(__name__) # load config from this file , mito.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'mito.db'),
    SECRET_KEY='iLikeThisCourseALotRightNow2016-2017',
    USERNAME='admin',
    PASSWORD='1234'
))
app.config.from_envvar('MITO_SETTINGS', silent=True)

curUser = None
pairNum = 0
timeDc = None

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

#@socketio.on('connect')
def connect():
	global timeDc
	timeDc = None
#    print("new connection: " + request.sid)

@socketio.on('disconnect')
def disconnect():
#    print('Client disconnected: ' + request.sid)
    global timeDc
    timeDc = time.time()

#def timeout():
#	with app.app_context():
#		while True:
#			timeNow = time.time()
#			if timeDc == None:
#				time.sleep(10)
#			else:
#				
#				if (timeNow - timeDc) > 30:
#					removeDBEntries()
#					break
#				else:
#					time.sleep(5)
#		print("dead " + curUser)

def removeDBEntries():
	db = get_db()
	con = db.cursor()
	global pairNum
	if type(pairNum) is tuple:
		pairNum = pairNum[0]

	otherUser = con.execute("SELECT name FROM users WHERE name NOT LIKE ? and pair=?", (curUser, pairNum)).fetchone()
	if otherUser:
		con.execute("UPDATE users SET pair=NULL WHERE name=?", (otherUser[0],))
		con.execute("DELETE FROM users WHERE name=?", (curUser,))
		con.execute("DELETE FROM pairs WHERE id=?", (pairNum,))
		db.commit()
#	DEV
		con.execute("SELECT * FROM users")
		for x in con:
			print(x)
	else:
		print("WTFFF")

def isPair(user1):
	"""
	Takes two user-objects as arguments

	Returns true if they are in a pair already
	"""
	db = get_db()
	con = db.cursor()

	partner = con.execute("SELECT name FROM users WHERE name=?", (user1,)).fetchone()
#	DEV
#	con.execute("SELECT * FROM users")
#	for x in con:
#		print(x)

	if partner:
		p_pair = con.execute("SELECT pair FROM users WHERE name=? and pair IS NOT NULL", (user1,)).fetchone()
		c_pair = con.execute("SELECT pair FROM users WHERE name=? and pair IS NOT NULL", (curUser,)).fetchone()
		print("Pairs")
		print(p_pair)
		print(c_pair)
		print(c_pair != p_pair)
		if c_pair != p_pair:
			#Paired with someone else!
			return 2
			
		else: 
			#pair does not exist, create pair
			if (not c_pair) and (not p_pair):
				#Create pairing
				con.execute("INSERT INTO pairs (name1, name2) VALUES (?, ?)", (user1,curUser) )
				db.commit()
				
				global pairNum
				if type(pairNum) is tuple:
					pairNum = pairNum[0]
	
				con.execute("UPDATE users SET pair=? WHERE name=? or name=?", (pairNum,user1,curUser) )
				db.commit()
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
	lon = request.form["lon"]
	lat = request.form["lat"]
	
	db = get_db()
	con = db.cursor()

	con.execute("UPDATE users SET locLon=?, locLat=? WHERE name=?", (lon,lat,curUser) )
	db.commit()
	
	global pairNum
	if type(pairNum) is tuple:
		pairNum = pairNum[0]



	userInput = con.execute("SELECT name FROM users WHERE name NOT LIKE ? and pair=?", (curUser,pairNum)).fetchone()
	if userInput == None:
		#ERROR!
		error="Pair no longer exists"
#		TODO CHECK THAT THE ADDED BELOW WORKS
		con.execute("DELETE FROM users WHERE name=?", (curUser,))
		db.commit()
		return render_template('/disconnect.html', error=error)

	locLat2, locLon2 = con.execute("SELECT locLat, locLon FROM users WHERE name=?", (userInput[0])).fetchone()
	if (locLat2 and locLon2):
		#return
		#return render_template('/meet.html', startLat=locLat1, startLon=locLon1, endLat=locLat2, endLon=locLon2, pair=pairnum, curUser=curUser)
		return render_template('/meet.html', startLat=lat, startLon=lon, endLat=locLat2, endLon=locLon2, url=url_for('meet'))
		
	else:
		#ERROR!
		error="Location data error"
		return render_template('/find_user.html', error=error, name=curUser)

@app.route("/meet")
def meet(error=None):
	time.sleep(10)
	return render_template('/loc.html')

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
	userInput = request.form["find_User"]
	db = get_db()
	con = db.cursor()

	pair = isPair(userInput)
	if pair == 1:
		#pair exists
		#get locs
		global pairNum
		pairNum = con.execute("SELECT pair FROM users WHERE name=? and pair IS NOT NULL", (curUser,)).fetchone()
		pairNum = pairNum[0]
		locLat1, locLon1 = con.execute("SELECT locLat, locLon FROM users WHERE name=?", (curUser,)).fetchone()
		locLat2, locLon2 = con.execute("SELECT locLat, locLon FROM users WHERE name=?", (userInput,)).fetchone()
#		print(locLat1, locLon1, locLat2, locLon2)
		print("Num and users")
		print(pairNum, curUser, userInput)
		if (locLat1 and locLon1 and locLat2 and locLon2):
			#return
		#	global thread
		#	if thread is None:
		#		thread = Thread(target=timeout)
		#		thread.start()
			return render_template('/meet.html', startLat=locLat1, startLon=locLon1, endLat=locLat2, endLon=locLon2, url=url_for('meet'))
			
		else:
			#ERROR!
			error="Location data error"
			return render_template('/find_user.html', error=error, name=curUser)
	elif pair == 2:
		error="User currently paired with someone else"
		return render_template('/find_user.html', error=error, name=curUser)
	else:
		#User not found, return to last page
		error="User not found"
		return render_template('/find_user.html', error=error, name=curUser)

#first is flipped!!!
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
	userInput = request.form["Username"]
	lon = request.form["lon"]
	lat = request.form["lat"]
	
	db = get_db()
	con = db.cursor()

	test = con.execute("SELECT id FROM users WHERE name=?", (userInput,)).fetchone()

	if test:
		return render_template("/index.html", error="User already exists")
		
	global curUser
	curUser = userInput
	con.execute("INSERT INTO users (name, locLon, locLat) VALUES (?, ?, ?)", (userInput,lon,lat) )
	db.commit()
	#render
	return render_template('/find_user.html', name=userInput)


if __name__ == '__main__':
	"""
	Main method
	"""
	
	#start
	socketio.run(app, debug=True)