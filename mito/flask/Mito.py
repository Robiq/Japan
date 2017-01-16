from flask import Flask, render_template, request, redirect, url_for
from User import *
from Pairing import *

app = Flask(__name__)


users=[]
pairs=[]

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
	return pair

def setUpMeeting(pair, user):
	#Double check pairing
	name = user.username
	if not (pair.hasUser(name)):
		return redirect("/", "Fatal error - user not a part of pair!")
	
	#TODO
	return pair.getLoc(name)

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

	partner = findUser(userInput)
	curUserObj = findUser(curUser)


	if partner != None:
		pairnr = pairExists(curUserObj, partner)
		if pairnr == -1:
			#Found user, create pairing!
			pairnr = addPair(curUserObj, partner)
		
		locs = setUpMeeting(pairnr, curUserObj)
		#PRINT nr 2 - needs correct formatting! send lat and lon as separate objects!!!
		loc1 = locs[0]
		loc2 = locs[1]
		#return TODO Can't send in pure location data
		return render_template('/meet.html', startLat=loc1[0], startLon=loc1[1], endLat=loc2[0], endLon=loc2[1])

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
	if userInput in users:
		return redirect("/", "User already exists")
	

	usr = User(userInput)
	users.append(usr)
	lon = request.form["lon"]
	lat = request.form["lat"]
	pos = request.form["pos"]
	print(lon)
	print("\n" + lat + "\n")
	usr.addCords(lon, lat, pos)

	#render

	return render_template('/find_user.html', name=userInput)


if __name__ == '__main__':
	"""
	Main method
	"""
	
	#start
	app.run(host='0.0.0.0', port=80)