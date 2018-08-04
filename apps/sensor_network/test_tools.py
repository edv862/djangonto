import requests
import random

def get_measures(url, sn, sensor):
    return requests.get(
        url + '/' + str(sn.id) + '/' + sensor.iri + '/'
    )

def send_measures(url, sn, sensor, measure):
    return requests.post(
        url + '/' + str(sn.id) + '/' + sensor.iri + '/',
        data=measure
    )

def send_random_measures(url, sn, sensor, times, low_limit=0, high_limit=0, event=None):
	if event:
		high_limit = event.measure_limit * 2

	count = 0
	while count < times:
		if sensor.measure_type == 'S':
			measure = {'measure': random.uniform(low_limit, high_limit)}
		elif sensor.measure_type == 'C':
			measure = {'lat': random.uniform(-90, 90),'lon': random.uniform(-180, 180)}
		else:
			measure = {'measure': random.uniform(low_limit, high_limit)}

		send_measures(url, sn, sensor, measure)
		count += 1
