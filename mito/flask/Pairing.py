class Pairing:
	pairs = 0

	def contains(username):
		return user1.isEqual(username) or user2.isEqual(username)

	def addCords(self):
		self.user1.addCords()
		self.user2.addCords()

	def meetingPoint(self):
		u1C=self.user1.getCords()
		u2C=self.user2.getCords()

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
