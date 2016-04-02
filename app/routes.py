from app import app, db
from flask import request, Response, jsonify

from .helpers import request_format_okay
from .models import User

@app.route('/')
def index():
	return "Hello World!"

@app.route('/usernamevalid', methods=['POST'])
def username_valid():
	if request_format_okay(request):
		data = request.get_json()
		user = User.query.filter_by(name=data["username"]).first()
		if user is None:
			return jsonify({'valid': True})
		else:
			return jsonify({'valid': False})
	else:
		return "415 Unsupported Media Type"