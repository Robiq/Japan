def findMidpoint(user, partner, con):
	"""
	Finds the middlepoint between two users
	Args:
	user : string
		username
	partner: string
		username
	con:
		cursor for the database
	Returns:
	float:
		Average longitude
	float:
		Average latitude
		
	"""
	#find loc user
	uLat, uLon = getLocUser(user, con)
	#find loc partner
	pLat, pLon = getLocUser(partner, con)
#	DEV
#	print(uLat, uLon, pLat, pLon)
	#calculate mean values
	meanLat = ((uLat + pLat) / 2)
	meanLon = ((uLon + pLon) / 2)
	#return mean
	return meanLon, meanLat

def insertPair(user, partner, db):
	"""
	Create a new pairing between two users

	Args:
	user : string
		username
	partner: string
		username
	db:
		database
	Returns:
		void
	"""
	con = db.cursor()
	midLon, midLat = findMidpoint(user, partner, con)
	con.execute("INSERT INTO pairs (name1, name2, mpLon, mpLat) VALUES (?, ?, ?, ?)", (user,partner, midLon, midLat) )
	db.commit()
#	DEV	
#	con.execute("SELECT * from pairs")
#	for x in con:
#		print(x)

def insertUser(user, lon, lat, db):
	"""
	Inserts a user into the users-table

	Args:
	user:string
		username
	lon: float
		longitude data
	lat: float
		latitude data
	db:
		database
	Returns:
		void
	"""
	con = db.cursor()
	con.execute("INSERT INTO users (name, locLon, locLat) VALUES (?, ?, ?)", (user,lon,lat) )
	db.commit()

def deleteUser(user, db):
	"""
	Delete user from the 'users'-table

	Args:
	user:string
		username 
	db;
		database
	Returns:
		void
	"""
	con = db.cursor()
	con.execute("DELETE FROM users WHERE name=?", (user,))
	db.commit()
#	DEV
#	print("Deleted " + user)

def updateMidpoint(user, partner, db):
	"""
	Updates the middlepoint between two users

	Args:
	user : string
		username
	partner: string
		username
	db:
		database
	Returns:
		void
	"""
	con = db.cursor()
	#Find middle-point
	midLon, midLat = findMidpoint(user, partner, con)
	#find pairing-ID
	pairNum = (getPairId(user, con))
	if(type(pairNum)) is tuple:
		pairNum = pairNum[0]
	con.execute("UPDATE pairs SET mpLon=?, mplat=? WHERE id=?",(midLon,midLat, pairNum))
	db.commit()

def updateLoc(user, lon, lat, db):
	"""
	Update the location data of a user

	Args:
	user : string
		username
	lon: float
		longitude data
	lat: float
		latitude data
	db:
		database
	Returns:
		void
	"""
	con = db.cursor()
	con.execute("UPDATE users SET locLon=?, locLat=? WHERE name=?", (lon,lat,user) )
	db.commit()

def updateUsers(user, partner, db):
	"""
	Update both users in a pair, with their pair-id

	Args:
	user:string
		username
	partner:string 
		username
	db:
		database
	Returns:
		void
	"""
	con = db.cursor()
	num = getPairId(user, con)[0]
#	DEV
#	print("PairID")
#	print(num)
	con.execute("UPDATE users SET pair=? WHERE name=?", (num,user))
	con.execute("UPDATE users SET pair=? WHERE name=?", (num,partner))
	db.commit()

def getMidLoc(user, con):
	"""
	Get the middle point between two users, from database

	Args:
	user:string
		Username
	con:
		cursor
	Returns:
	float:
		longitude
	float:
		latitude
	"""
	return con.execute("SELECT mpLon, mpLat FROM pairs WHERE name1=? OR name2=?", (user, user)).fetchone()

def getPairId(user, con):
	"""
	Find the correct id for a pair

	Args:
	user:string
		username
	con:
		cursor
	Returns:
	int:
		pair-id
	"""
	return con.execute("SELECT id FROM pairs WHERE name1=? OR name2=?", (user,user)).fetchone()

def getLocUser(user, con):
	"""
	Get the location data of a user

	Args:
	user:string
		username
	con:
		cursor
	Returns:
	float:
		longitude
	float:
		latitude
	"""
	return con.execute("SELECT locLat, locLon FROM users WHERE name=?", (user,)).fetchone()

def getPair(user, con):
	"""
	Get the pair-ID for the user

	Args:
	user:string
		username
	con:
		cursor
	Returns:
	int:
		pair-ID for the user
	"""
	return con.execute("SELECT pair FROM users WHERE name=? and pair IS NOT NULL", (user,)).fetchone()

def getPartner(user, con):
	"""
	Finds a users partner

	Args:
	user:string
		username
	con:
		cursor
	Returns:
	string:
		partners name
	"""
	pairNum = getPair(user, con)
	if(type(pairNum)) is tuple:
		pairNum = pairNum[0]
	return con.execute("SELECT name FROM users WHERE name NOT LIKE ? and pair=?", (user,pairNum)).fetchone()

def getUser(user, con):
	"""
	Find a user (check if he is in the database)
	Args:
	user:string
		username
	con:
		cursor
	Returns:
	string:
		users name
	"""
	return con.execute("SELECT name FROM users WHERE name=?", (user,)).fetchone()

#TODO handle session
def getTimeDc(user, con):
	"""
	Get disconnect time for user

	Args:
	user:string
		username
	con:
		cursor
	Returns:
	float:
		time of disconnect
	"""
	return con.execute("SELECT timeDc FROM users WHERE name=?", (user)).fetchone()

def setSID(user, sid, db):
	"""
	Set sessionID for a user
	Args:
	user:string
		username
	sid:float
		sessionID
	db:
		database
	Returns:
		void
	"""
	con = db.cursor()
	con.execute("UPDATE users SET sid=?, timeDc=NULL  WHERE name=?", (sid, user))
	db.commit()

def setTimeDc(sid, time, db):
	"""
	Set disconnect-time for sessionID

	Args:
	sid:int
		sessionID
	time:float
		time
	db:
		database
	Returns:
		void
	"""
	con = db.cursor()
	con.execute("UPDATE users SET timeDc=?  WHERE sid=?", (time, sid))
	db.commit()

#DEV
#Prints the whole database named 'name'
#def printDB(name, con):
#	query = "SELECT * FROM " + name
#	a = con.execute(query)
#	print(name)
#	for x in a:
#		print(x)
	
	
def removeDBEntries(user, db):
	"""
	Remove database-entry for user
	
	Args:
	user:string
		username
	db:
		database
	Returns:
		void
	"""
	con = db.cursor()
	otherUser = getPartner(user, con)
	#If user has a partner, delete pairing and user
	if otherUser:
		#find their pairing-number
		pairNum = getPair(user, con)
		#delete user
		deleteUser(user, db)
		if type(pairNum) is tuple:
			pairNum = pairNum[0]
		#delete pairing
		con.execute("DELETE FROM pairs WHERE id=?", (pairNum,))
		db.commit()
#		DEV
#		printDB("users", con)
#	else:
#		print("WTFFF")