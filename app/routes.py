from app import app, db
from flask import request, Response, jsonify, abort

from .helpers import request_format_okay
from .models import User

@app.route('/')
def index():
	return "Hello World!"

@app.route('/signin', methods=['POST'])
def signin():
	if request_format_okay(request):
		data = request.get_json()
		user = User.query.filter_by(name=data["username"]).first()
		if user is None:
			geo_string = str(data["lat"]) + " " + str(data["long"])
			new_user = User(name=data["username"], phone_number=data["phone_number"], geo=geo_string, radius=data["radius"])
			db.session.add(new_user)
			db.session.commit()
			return "200 OK"
		else:
			return abort(403)
	else:
		return abort(415)