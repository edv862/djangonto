import requests
import random
import concurrent.futures

import time

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from apps.sensor_network.models import SensorNetwork, BaseSensor, MeasureLog, AtomicEvent, Event

def get_measures(url, sn, sensor):
    return requests.get(
        url + '/' + str(sn.id) + '/' + sensor.iri + '/'
    )

def send_measures(url, sn, sensor, measure):
    return requests.post(
        url + '/' + str(sn.id) + '/' + sensor.iri + '/',
        data=measure
    )

def send_random_measures(url, sn, sensor, times=1, low_limit=0, high_limit=1, event=None):
    if event:
        high_limit = event.measure_limit * 2

    count = 0
    while count < times:
        if sensor.measure_type == 'S':
            measure = {'measure': random.randint(low_limit, high_limit)}
        elif sensor.measure_type == 'C':
            measure = {'lat': random.uniform(-90, 90),'lon': random.uniform(-180, 180)}
        else:
            measure = {'measure': random.uniform(low_limit, high_limit)}

        send_measures(url, sn, sensor, measure)
        count += 1

def send_concurrent_requests(sn, times=1, low_limit=0, high_limit=1):
    url = 'http://127.0.0.1:8000/sn'
    atomic_events = AtomicEvent.objects.exclude(cause=None)
    sensors = []

    for e in atomic_events:
        sensors.append(e.cause)

    time1 = time.time()
    for sensor in sensors:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as excecutor:
            future = excecutor.submit(
                send_random_measures, url, sn, sensor, times, low_limit, high_limit
            )
    time2 = time.time()
    total_time = (time2 - time1) * 1000.0
    all_sensors = len(sensors)
    print('took {:.3f} ms total, media: {:.3f}'.format(total_time, total_time/all_sensors))

# for testing import apps.sensor_network.test_tools
# apps.sensor_network.test_tools.send_concurrent_requests(SensorNetwork.objects.first(), BaseSensor.objects.get(iri='cel2'))
