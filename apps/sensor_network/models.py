import functools
from django.db import models

from model_utils import Choices
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
    measures = models.ManyToManyField('Measure')


class Measure(TimeStampedModel):
    value = models.CharField(max_length=25)


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

    def get_function(self):
        try:
            function = getattr(self, self.function)
            return functools.partial(function)
        except Exception as e:
            raise e

    def get_function_name(self):
        return self.function

    def __str__(self):
        return self.name + " - " + self.function


class AtomicEvent(Event):
    cause = models.ForeignKey('Sensor', on_delete=models.CASCADE)
    measure_limit = models.IntegerField(null=True, blank=True)

    def validate(self, sensor_input):
        function = self.get_function()
        result = function(sensor_input, self.measure_limit)

        if result:
            print("huehue")
        else:
            print("not hueheuhe")

        return result


class ComplexEvent(Event):
    events = models.ManyToManyField('Event', related_name='complex_event_events')
