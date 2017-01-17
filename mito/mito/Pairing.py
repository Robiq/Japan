class Pairing:
	pairs = 0

	def hasUser(self, username):
		return (self.user1.isEqual(username) or self.user2.isEqual(username))

	def addCords(self):
		self.user1.addCords()
		self.user2.addCords()

	def getLoc(self, uname):
		u1C = None
		u2C = None
		if self.user1.isEqual(uname):
			u1C=self.user1.getCords()
			u2C=self.user2.getCords()
		else:
			u1C=self.user2.getCords()
			u2C=self.user1.getCords()
			
		loc=[]
		loc.append(u1C)
		loc.append(u2C)
		return loc

	def __init__(self, user1, user2):
		self.user1 = user1
		self.user2 = user2
		self.name = user1.username + user2.username
		user1.addPairing(self)
		user2.addPairing(self)
		Pairing.pairs += 1
#Use Pairing to add information for both users.
#calculate meeting point TODO
#self.meetingPoint
