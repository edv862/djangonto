from django.db import models
from model_utils.models import TimeStampedModel


class LocationMap(models.Model):
    name = models.CharField(max_length=25)
    locations = models.ManyToManyField('Location', blank=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=25)
    coordinates = models.CharField(max_length=40, blank=True)
    extra_info = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class SensorNetwork(models.Model):
    name = models.CharField(max_length=25)
    sensors = models.ManyToManyField('Sensor', blank=True)
    events = models.ManyToManyField('Event', blank=True)

    def __str__(self):
        return self.name


class Sensor(models.Model):
    MEASURE_CHOICES = (
        ('S', 'Scalar'),
        ('B', 'Binary'),
        ('T', 'Text'),
        ('M', 'Misc'),
        # Multimedia data to go
    )
    name = models.CharField(max_length=25)
    measure_type = models.CharField(choices=MEASURE_CHOICES, max_length=6)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True)
    measures = models.ManyToManyField('Measure', blank=True)

    def __str__(self):
        return self.name


class Measure(TimeStampedModel):
    value = models.CharField(max_length=25)


class Event(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class AtomicEvent(Event):
    cause = models.ForeignKey('Sensor', on_delete=models.CASCADE)
    measure_limit = models.CharField(max_length=25)


class ComplexEvent(Event):
    events = models.ManyToManyField('Event', related_name='complex_event_events')