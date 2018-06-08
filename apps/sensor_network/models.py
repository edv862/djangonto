from django.db import models
from model_utils.models import TimeStampedModel


class LocationMap(models.Model):
	name = models.CharField(max_length=25)
	locations = models.ManyToManyField('Location')


class Location(models.Model):
	name = models.CharField(max_length=25)
	coordinates = models.CharField(max_length=40)
	extra_info = models.CharField(max_length=100)


class SensorNetwork(models.Model):
	name = models.CharField(max_length=25)
	sensors = models.ManyToManyField('Sensor')
	events = models.ManyToManyField('Event')


class Sensor(models.Model):
	MEASEURE_CHOICES = (
        ('S', 'Scalar'),
        ('B', 'Binary'),
        ('T', 'Text')
    )
	name = models.CharField(max_length=25)
	measure_type = models.CharField(choices=MEASEURE_CHOICES, max_length=6)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	measures = models.ManyToManyField('Measure', on_delete=models.CASCADE)


class Measure(TimeStampedModel):
	value = models.CharField(max_length=25)


class Event(models.Model):
	name = models.CharField(max_length=25)
	

class AtomicEvent(Event):
	cause = models.ForeignKey('Sensor', on_delete=models.CASCADE)
	measure_limit = models.CharField(max_length=25)


class ComplexEvent(Event):
	events = models.ManyToManyField('Event', related_name='complex_event_events')