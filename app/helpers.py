import os, string, random
import requests
import json
from math import asin, cos, sin, pi, sqrt
from twilio.access_token import AccessToken, IpMessagingGrant

EARTH_RAD = 3959.0

def request_format_okay(request):
	if request.headers['Content-Type'] == 'application/json':
		return True
	else:
		return False

def to_radians(degrees):
	return degrees*pi/180

def haversine(lat1, long1, lat2, long2):
	d = 2*EARTH_RAD*asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((long2-long1)/2)**2))
	return d

def generate_twilio_token(identity, device_id):
	account_sid = os.environ['TWILIO_ACCOUNT_SID']
	api_key = os.environ['TWILIO_API_KEY']
	api_secret = os.environ['TWILIO_API_SECRET']
	service_sid = os.environ['TWILIO_IPM_SERVICE_SID']

	endpoint = "MakeOrBreak:{0}:{1}".format(identity, device_id)

	token = AccessToken(account_sid, api_key, api_secret, identity)

	ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=service_sid)
	token.add_grant(ipm_grant)

	return token

def id_generator(size=30, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def create_bank_account(bank_object):
	print(bank_object)
	api_key = os.environ["CAPITALONE_API_KEY"]
	new_customer_url = 'http://api.reimaginebanking.com/customers?key={}'.format(api_key)
	new_customer_response = requests.post(new_customer_url, data=json.dumps(bank_object), headers={'content-type':'application/json'})
	
	if new_customer_response.status_code is not 201:
		print("Create customer failed")
		return 0

	customer_id = new_customer_response.json()["objectCreated"]["_id"]

	new_account_url = 'http://api.reimaginebanking.com/customers/{}/accounts?key={}'.format(customer_id, api_key)

	new_account_payload = {
		"type": "Checking",
		"nickname": "MakeOrBreak",
		"rewards": 0,
		"balance": 10000
	}

	new_account_response = requests.post(new_account_url, data=json.dumps(new_account_payload), headers={'content-type':'application/json'})

	if new_account_response.status_code != 201:
		print(new_account_response.json()["message"])
		return 0

	return new_account_response.json()["objectCreated"]["_id"]

def bank_transfer(payer_id, payee_id, amount):
	api_key = os.environ["CAPITALONE_API_KEY"]
	url = 'http://api.reimaginebanking.com/accounts/{}/transfers?key={}'.format(payer_id, api_key)

	payload = {
		"medium": "balance",
		"payee_id": payee_id,
		"amount": amount
	}

	transfer_response = requests.post(url, data=json.dumps(payload), headers={'content-type':'application/json'})

	if transfer_response.status_code == 201:
		return True
	else:
		print(transfer_response.json()["message"])
		return False
