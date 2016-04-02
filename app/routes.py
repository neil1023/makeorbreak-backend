from app import app, db
from flask import request, Response, jsonify, abort

from .helpers import request_format_okay
from .models import User, Request

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
			return jsonify({'id': new_user.id})
		else:
			return abort(403)
	else:
		return abort(415)

@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
	if request_format_okay(request):
		data = request.get_json()
		user = User.query.filter_by(name=data["username"]).first()
		geo_string = str(data["lat"]) + " " + str(data["long"])
		user.geo = geo_string
		db.session.commit()
		return "200 OK"
	else:
		return abort(415)

@app.route('/requests', methods=['POST'])
def new_request():
	if request_format_okay(request):
		data = request.get_json()
		user = User.query.filter_by(name=data["username"]).first()
		geo_string = str(data["request"]["lat"]) + " " + str(data["request"]["long"])
		new_request = Request(title=data["request"]["title"], description=data["request"]["description"], geo=geo_string)
		user.requests.append(new_request)
		db.session.add(new_request)
		db.session.commit()
		return "200 OK"
	else:
		return abort(415)
