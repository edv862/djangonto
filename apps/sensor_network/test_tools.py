import requests
import random
import concurrent.futures
import os
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
from itertools import chain
import numpy as np
import csv

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


def send_random_measures(url, sn, sensor, low_limit=0, high_limit=1, event=None):
    if event:
        high_limit = event.measure_limit * 2

    if sensor.measure_type == 'S':
        measure = {'measure': random.randint(low_limit, high_limit)}
    elif sensor.measure_type == 'C':
        measure = {'lat': random.uniform(-90, 90),'lon': random.uniform(-180, 180)}
    else:
        measure = {'measure': random.uniform(low_limit, high_limit)}

    return send_measures(url, sn, sensor, measure)


def send_concurrent_requests(sn, times=1, low_limit=0, high_limit=1):
    url = 'http://127.0.0.1:8000/sn'
    atomic_events = AtomicEvent.objects.exclude(cause=None)
    sensors = []

    for e in atomic_events:
        sensors.append(e.cause)

    all_sensors = len(sensors)
    time1 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        for sensor in sensors:
            futures = executor.map(
                send_random_measures,
                    (url for i in range(times)),
                    (sn for i in range(times)),
                    (sensor for i in range(times))
                )
            list(chain.from_iterable(futures))

    time2 = time.time()
    total_time = (time2 - time1) * 1000.0
    # print('took {:f} ms total, media: {:f} ms.'.format(total_time, total_time/all_sensors))
    return total_time, (total_time / all_sensors * times)


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
        count += 1

    count = 0
    while count < limit:
        if count < sensor_number:
            atomico = AtomicEvent(
                sn=sn,
                name=("atomic_" + str(count)),
                cause=sensor,
                function="true",
                duration=0,
            )
            atomico.save()
        else:
            atomico = AtomicEvent(
                sn=sn,
                name=("atomic_" + str(count)),
                cause=BaseSensor.objects.filter(sn=sn)[random.randint(0, sensor_number - 1)],
                function="true",
                duration=0,
            )
            atomico.save()

        if count > 1:
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

# Sensor number
# Sensor frequency
def running_tests(
        filename, tests_number, sensors_number_from, sensors_number_to,
        events_number, request_per_sensor=1
    ):
    sn = SensorNetwork.objects.all()[0]
    data_total = []
    
    print("Inicializando RSM para Pruebas")
    for i in range(sensors_number_from, sensors_number_to + 1, 10):
        # To make sure is not hung
        if i % 100 == 0:
            if i == 0:
                i = 1

            print(
                "Prueba numero " + str(i - sensors_number_from) + " con " + str(events_number) + " Eventos " +
                str(i) + " Sensores"
            )

        if sensors_number_from == 0 and i == 0:
            i = 1

        sensorWithEventGenerator(
            sn, -(-i // 2), -(-i // 2),
            0, events_number, events_number
        )
        
        total = 0
        average = 0
        for j in range(0, tests_number):
            print('outside ' + str(j))
            aux_total, aux_average = send_concurrent_requests(sn, times=request_per_sensor)
            total += aux_total
            average += aux_average

        # Append tiempo total, promedio, numero de sensores atomico
        # numero de sensores movibles, numero de eventos atomicos, numero de eventos complejos.
        data_total.append(
            (
                total/tests_number, average/tests_number,
                i, events_number*2
            )
        )

    print("Iniciando escritura en archivo.")
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["Tiempo total(ms)", "Promedio(ms)", "Sensores", "Eventos", "Request a Sensor por Prueba"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for d in data_total:
            writer.writerow(
                {
                  'Tiempo total(ms)': str(d[0]),
                  'Promedio(ms)': str(d[1]),
                  'Sensores': str(d[2]),
                  'Eventos': str(d[3]),
                  'Request a Sensor por Prueba': str(request_per_sensor)
                }
            )

    print("Finalizado proceso de pruebas.")

def plot_test_files(filenames, y_column=1, x_column=-1, delimiter=','):
    # x == -1 indicates to count the xs axis to fill the y axis
    xs = [] # x axis
    ys = [] # y axis

    for filename in filenames: 
        first = True
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            for line in f:
                if not first:
                    line_data = line.split(delimiter)
                    xs.append(float(line_data[x_column]))
                    ys.append(float(line_data[y_column]))
                
                first = False

    ax = plt.subplot(111)
    if x_column != -1:
        plt.plot(xs, ys)
    else:
        plt.plot(range(len(ys)), ys)

    plt.show()

# Graph if points inside an array of polygos
# radius < 0 indicates if the points are in clockwise orders or not (radius > 0)
def graph_points_in_polygon(points=[], polygons=[], radius=-0.1):
# Example of usage
    sala = patches.Polygon(
        np.array([
            [1,1],
            [1,2],
            [3,2],
            [3,1],
            [1,1]
        ]), True, color='blue')
    pas1 = patches.Polygon(
        np.array([
            [2,2],
            [2,5],
            [3,5],
            [3,3],
            [7,3],
            [7,2],
            [2,2]
        ]), True, color='green')
    pas2 = patches.Polygon(
        np.array([
            [2,5],
            [2,6],
            [7,6],
            [7,3],
            [6,3],
            [6,5],
            [2,5]
        ]), True, color='grey')
    points = [
        (1,1), (1,4,1,3), (1.8,2), (0.8, 0.8), (3.5, 3.4), (4,2.4), (6.5, 3), (6.6, 6.3), (1.7, 2.3), (5.3, 5.2), (2.5, 5.3), (5.4, 2.5),
        (6.8, 4.2), (2.8, 1.6), (3.5, 2.5), (2.6, 4.7), (3, 2.7), (3.9, 6), (5.2, 6.7), (2.5, 3.8), (2, 1.5), (4, 5.5), (6.5, 5.5)
    ]

    fig,ax = plt.subplots()

    for polygon in polygons:
        polygons.append(patches.Polygon(np.array(polygon)))

    polygons.append(sala)
    polygons.append(pas1)
    polygons.append(pas2)

    colors = 100*np.random.rand(len(polygons))
    p = PatchCollection(polygons)
    ax.add_collection(p)

    for point in points:
        if any([polygon.contains_point(point, radius=radius) for polygon in polygons]):
            ax.scatter(point[0],point[1], color="green", zorder=6)
        else:
            ax.scatter(point[0],point[1], color="crimson", zorder=6)

    ax.scatter(4.2, 5.3, color="crimson", zorder=6)
    ax.scatter(2.5, 1.8, color="crimson", zorder=6)

    p.set_array(np.array(colors))
    plt.show()


# for testing purposes
# import apps.sensor_network.test_tools as ttools
# for i in range(1, 11):
#  ttools.running_tests('tests_results/1000s_1000ev_' + str(1000*i) + 'req.csv', 10, 500, 500, 500, 1000*i)
# ttools.running_tests('tests_results/test_data.csv', 5, 300, 310, 500, 1)
# ttools.plot_test_files(['tests_results/1000ev_1000s_1req.csv'])
# ttools.graph_points_in_polygon()