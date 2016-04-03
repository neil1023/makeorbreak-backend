from app import app, db
from flask import request, Response, jsonify, abort
from clarifai.client import ClarifaiApi
import base64
import tinys3

from .helpers import request_format_okay, to_radians, haversine, generate_twilio_token, create_bank_account, bank_transfer
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
			
			bank_object = {"first_name":data["first_name"], "last_name":data["last_name"], "address":data["address"]}
			account_id = create_bank_account(bank_object)

			geo_string = str(data["lat"]) + " " + str(data["long"])			
			new_user = User(name=data["username"], phone_number=data["phone_number"], geo=geo_string, radius=data["radius"], device_id=data["device_id"], account_id=account_id)
			db.session.add(new_user)
			db.session.commit()

			identity = new_user.name
			device_id = new_user.device_id

			token = generate_twilio_token(identity, device_id)

			return jsonify({'id': new_user.id, 'username': identity, 'token': token.to_jwt()})
		else:
			return abort(403)
	else:
		return abort(415)

@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    if request_format_okay(request):
        data = request.get_json()
        user = User.query.get(data["user_id"])
        geo_string = str(data["lat"]) + " " + str(data["long"])
        user.geo = geo_string
        db.session.commit()
        return jsonify({'id': user.id})
    else:
        return abort(415)

@app.route('/clarifai', methods=['POST'])
def clarifai():
    if request_format_okay(request):
        data = request.get_json()
        request_id = Request.query.get(data["request_id"])
        image_encoded = str(data["image_encoded"] + "")
        db.session.commit()

        fh = open("imageToSave.png", "wb")
        fh.write(base64.b64decode(image_encoded))
        fh.close()

        conn = tinys3.Connection("AKIAIX6NSVB22AGEHNDQ","2MNcMkJIxLiJxAl7B5mwxjrIBmpQru4ODsKKNCDN",tls=True)
        f = open('imageToSave.png','rb')
        conn.upload('imageToSave.png',f,'make-or-break')
        f.close()

        clarifai_api = ClarifaiApi() # assumes environment variables are set
        result = clarifai_api.tag_images(open('./imageToSave.png', 'rb'))
        return result
    else:
        return abort(415)

@app.route('/requests', methods=['POST'])
def new_request():
	if request_format_okay(request):
		data = request.get_json()
		user = User.query.get(data["user_id"])
		geo_string = str(data["request"]["lat"]) + " " + str(data["request"]["long"])
		new_request = Request(title=data["request"]["title"], description=data["request"]["description"], geo=geo_string, price=data["request"]["price"])
		print(new_request)
		user.requests.append(new_request)
		db.session.add(new_request)
		db.session.commit()
		return jsonify({'id': new_request.id})
	else:
		return abort(415)

@app.route('/requests/<int:request_id>', methods=['PUT'])
def update_request(request_id):
    if request_format_okay(request):
        data = request.get_json()
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
    else:
        return abort(415)

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
	requests = Request.query.filter_by(claimed=-1)
	response = {"requests":[]}
	for r in requests:
		[req_lat, req_long] = [to_radians(float(x)) for x in r.geo.split(" ")]
		d = haversine(user_lat, user_long, req_lat, req_long)
		print(d)
		if d <= user_radius:
			response["requests"].append(r.as_dict())
	return jsonify(response)

@app.route('/requests/<int:request_id>/claim', methods=['POST'])
def claim(request_id):
	if request_format_okay(request):
		data = request.get_json()
		user = User.query.get(data["user_id"])
		req = Request.query.get(request_id)
		req.claimed = user.id
		db.session.commit()
		return jsonify({"breaker_username": User.query.get(req.user_id).name, "username": user.name})
	else:
		return abort(415)

@app.route('/requests/<int:request_id>/claim/cancel', methods=['POST'])
def cancel_claim(request_id):
	req.claimed = -1
	db.session.commit()
	return "200 OK"

@app.route('/requests/<int:request_id>/claim/complete', methods=['POST'])
def complete_claim(request_id):
	if request_format_okay(request):	
		data = request.get_json()
		req = Request.query.get(request_id)

		fixer = User.query.filter_by(name=data["username"]).first()
		breaker = User.query.get(req.user_id)
		
		if bank_transfer(breaker.account_id, fixer.account_id, req.price):		
			db.session.delete(req)
			db.session.commit()
			return "200 OK"
		else:
			return abort(500)
	else:
		return abort(415)