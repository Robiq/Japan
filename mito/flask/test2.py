from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@app.route("/")
def renderBase(error=None):
	"""
	Returns the rendered template of the base-page
	"""
	return render_template('init.html')

if __name__ == '__main__':
    socketio.run(app)