from app import app, db
from flask import request, Response, jsonify, abort

from .helpers import request_format_okay, to_radians, haversine
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
		return jsonify({'id': new_request.id})
	else:
		return abort(415)

@app.route('/requests/<int:request_id>', methods=['PUT'])
def update_request(request_id):
	data = request.get_json
	req = Request.query.get(request_id)
	geo_string = str(data["lat"]) + " " + str(data["long"])	
	if data["title"] != req.title:
		req.title = data["title"]
	if data["description"] != req.description:
		req.description = data["description"]
	if geo_string != req.geo:
		req.geo = geo_string
	db.session.commit()
	return "200 OK"

@app.route('/requests/<int:request_id>', methods=['DELETE'])
def delete_request(request_id):
	req = Request.query.get(request_id)
	db.session.delete(req)
	db.session.commit()
	return "200 OK"

@app.route('/users/<int:user_id>/requests', methods=['GET'])
def get_requests(user_id):
	user = User.query.get(user_id)
	[user_lat, user_long] = [to_radians(float(x)) for x in user.geo.split(" ")]
	user_radius = user.radius
	requests = Request.query.all()
	response = {"requests":[]}
	for r in requests:
		[req_lat, req_long] = [to_radians(float(x)) for x in r.geo.split(" ")]
		d = haversine(user_lat, user_long, req_lat, req_long)
		print(d)
		if d <= user_radius:
			response["requests"].append(r.as_dict())
	return jsonify(response)