from math import asin, cos, sin, pi, sqrt

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