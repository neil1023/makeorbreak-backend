from app import app, db
from flask import json, request, Response

@app.route('/')
def index():
	return "Hello World!"
