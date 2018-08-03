import requests

def get_measures(url, sn, sensor):
    return requests.get(
        url + '/' + str(sn.id) + '/' + sensor.iri + '/'
    )

def send_measures(url, sn, sensor, measure):
    return requests.post(
        url + '/' + str(sn.id) + '/' + sensor.iri + '/',
        data=measure
    )