from app import app, db
from flask import request, Response, jsonify, abort
from clarifai.client import ClarifaiApi
import base64
import tinys3
import os

from .helpers import request_format_okay, to_radians, haversine, generate_twilio_token, id_generator, create_bank_account, bank_transfer, add_tag_to_user, remove_tag_from_user, generate_keywords, add_tag_to_request, remove_tag_from_request
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

            new_user = User(name=data["username"], phone_number=data["phone_number"], lat=data["lat"], lon=data["long"], radius=data["radius"], device_id=data["device_id"], account_id=account_id)

            db.session.add(new_user)
            for tag in data["tags"]:
                add_tag_to_user(new_user, tag)

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
        user.lat = data["lat"]
        user.lon = data["long"]
        db.session.commit()
        return jsonify({'id': user.id})
    else:
        return abort(415)

@app.route('/clarifai', methods=['POST'])
def clarifai():
    if request_format_okay(request):
        s3_base_url = 'https://make-or-break.s3.amazonaws.com/'
        data = request.get_json()
        request_obj = Request.query.get(data["request_id"])
        image_url = str(data["image_encoded"] + "")
        file_type = data["file_type"] if data["file_type"] else ".png"

        fileName = id_generator() + "." + file_type
        fh = open(fileName, "wb")
        fh.write(base64.b64decode(image_url))
        fh.close()

        aws_key = os.environ.get('AWS_KEY')
        aws_secret = os.environ.get('AWS_SECRET')
        conn = tinys3.Connection(aws_key, aws_secret, tls=True)
        f = open(fileName, 'rb')
        conn.upload(fileName, f, 'make-or-break')
        f.close()

        s3_url = s3_base_url + fileName

        request_obj.image_url = s3_url
        db.session.commit()

        os.remove(fileName)

        clarifai_api = ClarifaiApi() # assumes environment variables are set
        result = clarifai_api.tag_image_urls(s3_url)
        return jsonify(result)
    else:
        return abort(415)

@app.route('/requests', methods=['POST'])
def new_request():
    if request_format_okay(request):
        data = request.get_json()
        user = User.query.get(data["user_id"])
        new_request = Request(title=data["request"]["title"], description=data["request"]["description"], lat = data["request"]["lat"], lon=data["request"]["long"], price=data["request"]["price"])

        tags = generate_keywords(data["request"]["title"], data["request"]["description"])

        user.requests.append(new_request)

        db.session.add(new_request)
        for (tag, value) in tags:
            add_tag_to_request(new_request, tag)

        db.session.commit()
        return jsonify({'id': new_request.id})
    else:
        return abort(415)

@app.route('/requests/<int:request_id>', methods=['PUT'])
def update_request(request_id):
    if request_format_okay(request):
        data = request.get_json()
        req = Request.query.get(request_id)
        if data["title"] != req.title:
            req.title = data["title"]
        if data["description"] != req.description:
            req.description = data["description"]
        if data["lat"] != req.lat:
            req.lat = data["lat"]
        if data["long"] != req.lon:
            req.lon = data["long"]
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

@app.route('/requests/<int:request_id>/tags/update', methods=['POST'])
def update_request_tags(request_id):
    if request_format_okay(request):
        data = request.get_json()
        req = Request.query.get(request_id)
        for tag in data:
            if tag["operation"] == "remove":
                remove_tag_from_request(req, tag["tag"])
            else:
                add_tag_to_request(req, tag["tag"])
        db.session.commit()
        return "200 OK"
    else:
        return abort(415)

@app.route('/users/<int:user_id>/requests', methods=['GET'])
def get_requests(user_id):
    requests = Request.query.filter_by(user_id=user_id)
    response = {"requests":[]}
    for r in requests:
        response["requests"].append(r.as_dict())
    return jsonify(response)

@app.route('/users/<int:user_id>/requests/local', methods=['GET'])
def get_local_requests(user_id):
    user = User.query.get(user_id) 
    user_radius = user.radius
    requests = Request.query.filter_by(claimed=-1)
    response = {"requests":[]}
    for r in requests:
        d = haversine(user.lat, user.lon, r.lat, r.lon)
        # print(d)
        if d <= user_radius:
            response["requests"].append(r.as_dict())
    print(response)
    return jsonify(response)

@app.route('/users/<int:user_id>/requests/claimed', methods=['GET'])
def get_claimed_requests(user_id):
    requests = Request.query.filter_by(claimed=user_id)
    response = {"requests":[]}
    for r in requests:
        response["requests"].append(r.as_dict())
    return jsonify(response)

@app.route('/users/<int:user_id>/tags/update', methods=['POST'])
def update_user_tags(user_id):
    if request_format_okay(request):
        data = request.get_json()
        user = User.query.get(user_id)
        for tag in data:
            if tag["operation"] == "remove":
                remove_tag_from_user(user, tag["tag"])
            else:
                add_tag_to_user(user, tag["tag"])
        db.session.commit()
        return "200 OK"
    else:
        return abort(415)

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

