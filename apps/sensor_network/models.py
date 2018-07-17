import functools
from django.db import models

from model_utils import Choices
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
        ('C', 'Coord'),
        # Multimedia data to go
    )
    iri = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=25)
    measure_type = models.CharField(choices=MEASURE_CHOICES, max_length=6)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True)

    def validate_input(self, sensor_input):
        """
        Sends input to validate with events.
        So far validates only scalar values (integer),and text.
        """
        result = []
        events = self.events.all()
        for event in events:
            if event.validate(sensor_input):
                result.append(event)

        return result

    def get_measure_type(self):
        return self.measure_type

    def __str__(self):
        return self.name


class MeasureLog(TimeStampedModel):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='measure_log'
    )
    # interest = models.BooleanField(default=False)
    value = models.CharField(max_length=100)

    def coordenate(self):
        """
        Returns value as tuple (lat,lon).
        """
        aux = self.value.split(',')
        lat = aux[0]
        lon = aux[1]
        return (lat, lon)

    def integer(self):
        """
        Returns value as integer
        """
        return int(self.value)

    def get_value(self):
        if self.sensor.get_measure_type() == 'C':
            return self.coordenate()
        elif self.sensor.get_measure_type() == 'S':
            return self.integer()
        else:
            return self.integer()


class Event(models.Model):
    FUNCTIONS = Choices(
        "less_than",
        "great_than",
        "less_than_equal",
        "great_than_equal",
        "not_less_than",
        "not_great_than",
        "not_less_than_equal",
        "not_great_than_equal",
        "equal",
        "not_equal",
    )

    name = models.CharField(max_length=25)

    function = models.CharField(
        max_length=25,
        choices=FUNCTIONS,
        default=FUNCTIONS.less_than
    )

    def less_than(self, op1, op2):
        return (op1 < op2)

    def great_than(self, op1, op2):
        return (op1 > op2)

    def less_than_equal(self, op1, op2):
        return (op1 <= op2)

    def great_than_equal(self, op1, op2):
        return (op1 >= op2)

    def not_less_than(self, op1, op2):
        return (op1 >= op2)

    def not_great_than(self, op1, op2):
        return (op1 <= op2)

    def not_less_than_equal(self, op1, op2):
        return (op1 > op2)

    def not_great_than_equal(self, op1, op2):
        return (op1 < op2)

    def equal(self, op1, op2):
        return (op1 == op2)

    def not_equal(self, op1, op2):
        return (op1 != op2)

    def get_function(self):
        try:
            function = getattr(self, self.function)
            return function
        except Exception as e:
            raise e

    def get_function_name(self):
        return self.function

    def __str__(self):
        return self.name + " - " + self.function


class AtomicEvent(Event):
    cause = models.ForeignKey(
        'Sensor',
        on_delete=models.CASCADE,
        related_name='events'
    )
    measure_limit = models.IntegerField(null=True, blank=True)

    def validate(self, sensor_input):
        """
        Applies designated event function to the value given
        by the sensor and the measure_limit.
        """
        function = self.get_function()
        result = function(sensor_input, self.measure_limit)

        return result


class ComplexEvent(Event):
    events = models.ManyToManyField('Event', related_name='complex_event_events')
