import sqlite3 as sql
import os
from flask import *
from User import *
from Pairing import *

app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , flaskr.py

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

#Find the correct user based on name
def findUser(userName):
	"""
	Takes a username as argument

	Returns None if not present, else returns User-object
	"""
	for u in users:
		if u.isEqual(userName):
			return u

	return None

def pairExists(user1, user2):
	"""
	Takes two user-objects as arguments

	Returns true if they are in a pair already
	"""
	if user1.paired == user2.paired and user1.paired != None:
		return pairs.index(user1.paired)
	return -1

def addPair(user1, user2):
	"""
	Takes two user-objects as arguments

	Returns a new pair-object
	"""
	pair = Pairing(user1, user2)
	pairs.append(pair)
	return pairs.index(user1.paired)

def setUpMeeting(pair, user):
	#Double check pairing
	name = user.username
	if not (pairs[pair].hasUser(name)):
		return redirect("/", "Fatal error - user not a part of pair!")
	
	#TODO
	return pairs[pair].getLoc(name)

	#show map and points
	#google map API functions


	#Find median
	#pair.metingPoint()
	
	#Show route to median and ETA
	#Show other person and their ETA

@app.route("/")
def renderBase(error=None):
	"""
	Returns the rendered template of the base-page
	"""

	return render_template('index.html', error=error)

#@app.route("/meet")
#def meet(pair, person, error=None):
	"""
	Renders the page for the actual functionality. 

	Args:
		None
	Returns:
		Redirects back to the original page, after handling the input.
	Raises:
		None
	"""
	#Sleep
#	sleep(10)
	#Call getLoc for person
	#After handling getLoc for person,
	#rerender meet with new info

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
	#
	userInput = request.form["find_User"]
	curUser = request.form["cur_User"]

	db = get_db()
	con = db.cursor()

	partner = con.execute("SELECT name FROM users WHERE name=?", (userInput)).fetchone()
	curUserObj= con.execute("SELECT name FROM users WHERE name=?", (curUser)).fetchone()

	if partner and curUserObj:
		p_pair = con.execute("SELECT pair FROM users WHERE name=? and pair IS NOT NULL", (userInput)).fetchone()
		c_pair = con.execute("SELECT pair FROM users WHERE name=? and pair IS NOT NULL", (curUser)).fetchone()
		
		if c_pair != p_pair:
			#Paired with someone else!
			#User not found, return to last page
			error="User currently paired with someone else"
			return render_template('/find_user.html', error=error, name=curUser)
		else: 
			#pair does not exist
			if (not c_pair) and (not p_pair):
				#Create pairing
				con.execute("INSERT INTO pairs (name1, name2) VALUES (?, ?)", (userInput,curUser) )
				db.commit()
				pairNr = con.execute("SELECT id FROM pairs WHERE name1=? OR name2=?", (curUser,curUser)).fetchone()
				con.execute("UPDATE users SET pair=? WHERE name=? or name=?", (pairNr[0],userInput, curUser) )
				#con.execute("INSERT INTO users (pair) VALUES (?) WHERE name=?", (pairNr,curUser) )
				db.commit()
				con.execute("SELECT * FROM users")
				for x in con:
					print(x)

			#pair exists
			#get locs
			locLat1, locLon1 = con.execute("SELECT locLat, locLon FROM users WHERE name=?", (curUser)).fetchone()
			locLat2, locLon2 = con.execute("SELECT locLat, locLon FROM users WHERE name=?", (userInput)).fetchone()
			if (locLat1 and locLon1 and locLat2 and locLon2):
				#return
				return render_template('/meet.html', startLat=locLat1, startLon=locLon1, endLat=locLat2, endLon=locLon2)
			else:
			#ERROR!
				print("WTF")

	else:
		#User not found, return to last page
		error="User not found"
		return render_template('/find_user.html', error=error, name=curUser)


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
	pos = request.form["pos"]
	
	db = get_db()
	con = db.cursor()

	test = con.execute("SELECT * FROM users WHERE name=?", (userInput)).fetchone()

	if test:
		return redirect("/", "User already exists")
		

	con.execute("INSERT INTO users (name, locLon, locLat) VALUES (?, ?, ?)", (userInput,lon,lat) )
	db.commit()
	#render
	return render_template('/find_user.html', name=userInput)


if __name__ == '__main__':
	"""
	Main method
	"""
	
	#start
	app.run()