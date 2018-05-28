import json

from django.shortcuts import render
from urllib import request as urlrequest
from ipware import get_client_ip
from .utils import log, getTime

def index(request):
	ip_list = [
		{'location': 'Your Current IP address',
		'ip': get_client_ip(request)[0]},
		{'location': 'Humboldt University',
		'ip': '141.20.5.218'},
		{'location': 'TorGuard/New York',
		'ip': '88.202.178.99'},
		{'location': 'TorGuard/Miami',
		'ip': '173.44.37.98'},
		{'location': 'TorGuard/Stockholm',
		'ip': '46.246.124.91'},
		{'ip': 'reddit.com'},
		{'ip': 'wikipedia.org'},
		{'ip': 'spiegel.de'},
	]
	context = {'ips': ip_list}
	return render(request, 'index.html', context)

def detail(request, ip_addr):
	context = {
		'ip': ip_addr
	}

	success_msg = 'Success! Response from server:'
	unsplash_access_key = '7c137985bea8fc7a95af7f31fa4fe4e253c56b0279b531afd2d3a71944fb74a9'
	owm_access_key = '624de6c8a414938f4f2a5071da02e0db'


	#get location information for a given ip address:
	location_rest_url = 'http://ip-api.com/json/%s' % ip_addr
	log('\nGET %s' % location_rest_url, 'yellow')

	with urlrequest.urlopen(location_rest_url) as resource:
		charset = resource.headers.get_content_charset()
		response = resource.read().decode(charset)

	data = json.loads(response)
	status = data['status']

	if status == 'success':
		log(success_msg, 'green')
		log(data, 'white')

		lat = data['lat']
		lon = data['lon']
		city = data['city']
		country = data['country']

		timezone = data['timezone']
		
		context['time'] = getTime(timezone)
		context['city'] = city
		context['country'] = country

		context['lat'] = lat
		context['lon'] = lon

	else:
		error_msg = 'ip-api.com returned an error: %s' % data['message']
		log(error_msg, 'red')
		context['error'] = error_msg
		return render(request, 'index.html', context)


	#get background image for a given location via unsplash:	
	unsplash_city = city.replace(" ", "+") #replace spaces in city name for use in url

	unsplash_rest_url = 'https://api.unsplash.com/search/photos/?query=%s&per_page=1&client_id=%s' % (unsplash_city, unsplash_access_key)
	log('\nGET %s' % unsplash_rest_url, 'yellow')

	with urlrequest.urlopen(unsplash_rest_url) as resource:
		charset = 'UTF-8'
		response = resource.read().decode('UTF-8')

	data = json.loads(response)
	if 'errors' in data:
		error_msg = 'api.unsplash.com returned an error: %s' % data['errors']
		log(error_msg, 'red')
		context['error'] = error_msg
		return render(request, 'index.html', context)

	else:
		log(success_msg, 'green')
		log(data,'white')
		
		bg_url = data['results'][0]['urls']['regular']
		context['bg_url'] = bg_url


	#get weather forecast for today based on location:
	owm_rest_url = 'https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&APPID=%s' % (lat, lon, owm_access_key)
	log('\nGET %s' % owm_rest_url, 'yellow')

	with urlrequest.urlopen(owm_rest_url) as resource:
		charset = 'UTF-8'
		response = resource.read().decode('UTF-8')

	data = json.loads(response)
	
	if 'message' in data:
		error_msg = 'api.openweathermap.org returned an error: %s' % data['message']
		log(error_msg, 'red')
		context['error'] = error_msg
		return render(request, 'index.html', context)

	else:
		log(success_msg, 'green')
		log(data,'white')
		temp_in_k = data['main']['temp']
		temp = round(temp_in_k - 273.15, 1)

		context['temp'] = temp

	#get map with marker from google maps:

	return render(request, 'index.html', context)