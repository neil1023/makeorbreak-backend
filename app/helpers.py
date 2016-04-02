def request_format_okay(request):
	if request.headers['Content-Type'] == 'application/json':
		return True
	else:
		return False
