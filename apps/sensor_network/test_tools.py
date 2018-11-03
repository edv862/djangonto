import requests
import random
import concurrent.futures

import time

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from apps.sensor_network.models import (
    SensorNetwork, BaseSensor,
    MeasureLog, AtomicEvent,
    ComplexEvent, Event,
    Sensor
)


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


# Function to create n sensors callet 'sensor' + index related to the sensor network sn
# with 'moveable_number' of them been moveable
def sensorWithEventGenerator(sn, sensor_number=0, moveable_number=0, start_index=0, atomic_events=0, complex_events=0):
    Sensor.objects.all().delete()
    count = start_index
    limit = start_index + sensor_number
    last_event = None

    while count < limit:
        sensor = Sensor(
            sn=sn,
            iri="s_" + str(count),
            name="sensor_" + str(count),
            measure_type='S',
            location=sn.location_map.locations.all()[random.randint(0, len(sn.location_map.locations.all()) - 1)]
        )

        if(count < start_index + moveable_number):
            sensor.is_moveable = True
            sensor.iri = "ms_" + sensor.iri
            sensor.name = "moveable_" + str(count)

        sensor.save()

        atomico = AtomicEvent(
            sn=sn,
            name=("atomic_" + str(count)),
            cause=sensor,
            function="true",
            duration=0,
        )
        atomico.save()

        if count > start_index + 1:
            complejo = ComplexEvent(
                sn=sn,
                name=("complex_" + str(count)),
                first_event=last_event,
                second_event=atomico,
                function="overlaps",
                is_complex=True,
                duration=0,
            )
            complejo.save()

        last_event = atomico
        count += 1


# for testing import apps.sensor_network.test_tools as ttools
# apps.sensor_network.test_tools.send_concurrent_requests(SensorNetwork.objects.first(), BaseSensor.objects.get(iri='cel2'))
# import apps.sensor_network.test_tools as ttools
# from apps.sensor_network.models import *
# sensor_network = SensorNetwork.objects.all()[0]
