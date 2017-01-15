from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/findLongLat", methods=['POST'])
def findLongLat():
	#Make sure the method used is post.
	assert request.method == 'POST'

	lat = request.form["LocLat"]
	lon = request.form["LocLong"]

	print(lat)

@app.route("/")
def renderBase(error=None):
	"""
	Returns the rendered template of the base-page
	"""
	return render_template('findLongLat.html', error=error)

if __name__ == '__main__':
	"""
	Main method
	"""
	
	#start
	app.run()