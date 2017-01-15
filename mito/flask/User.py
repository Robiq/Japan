import requests
import geocoder

class User:
	userCount = 0

	def displayCount(self):
		print "Total Users %d" % User.userCount

	def addPairing(self, Pairing):
		self.paired = Pairing

	def addCords(self, lon, lat):
		self.coords{}
		coords['lat'] = lat
		coords['lon'] = lon

	def getCords(self):
		return self.coords

	def displayEmployee(self):
		print "Username : ", self.username,  ", Connection: ", self.connection

	#If this object has the same name as the argument, return true. Else return false.
	def isEqual(self, uName):
		if uName == self.username:
			return True
		return False

	#def popLoc():
	"""
	Pop-up for accepting connection to another user and giving access to GPS-cordinates
	"""


	def __init__(self, username):
		self.username = username
		self.paired = None
		User.userCount += 1