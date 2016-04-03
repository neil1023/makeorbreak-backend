import os, string, random
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