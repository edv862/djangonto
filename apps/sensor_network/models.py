import functools
import math

from django.core.cache import cache
from django.db import models

from model_utils import Choices
from model_utils.models import TimeStampedModel


class LocationMap(models.Model):
    name = models.CharField(max_length=25)
    locations = models.ManyToManyField('Location', blank=True)

    def __str__(self):
        return self.name

    def get_location(self, sensor=None, measure=None):
        if sensor and not measure:
            if sensor.is_moveable:
                measure = MeasureLog.objects.filter(sensor=sensor).last()
                if measure:
                    measure = measure.get_coordinates()
            else:
                measure = sensor.location.get_coordinates()
        elif not measure and not sensor:
            return None

        loc = []
        min_dist = 0
        for location in self.locations.all():
            coord1 = location.get_coordinates()
            coord2 = measure.get_coordinates()
            distance = math.sqrt(
                math.pow(coord1[0] - coord2[0], 2) +
                math.pow(coord1[1] - coord2[1], 2)
            )
            if loc:
                if distance < min_dist:
                    loc = [location]
                    min_dist = distance
                elif distance == min_dist:
                    loc.append(location)
            else:
                loc = location
                min_dist = distance

        return (loc, min_dist)


class Location(models.Model):
    name = models.CharField(max_length=25)
    coordinates = models.CharField(max_length=40, blank=True)
    extra_info = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    def get_coordinates(self):
        """
        Returns value as tuple (lat,lon).
        """
        aux = self.value.split(',')
        lat = aux[0]
        lon = aux[1]
        return (lat, lon)


class SensorNetwork(models.Model):
    name = models.CharField(max_length=25)
    location_map = models.ForeignKey(
        'LocationMap',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def get_location(self, sensor=None, measure=None):
        return self.location_map.get_location(self, sensor, measure)

    def check_complex_queue(self):
        l = []
        for cpx_event in self.event_set.filter(is_complex=True):
            if cache.get(cpx_event.name):
                l.append(cpx_event)

        return l

    def update_compleX_queue(self):
        for cpx_event in self.event_set.filter(is_complex=True):
            if cpx_event.is_happening():
                cache.set(cpx_event.name + '_seq', True, cpx_event.duration + 10)
                cache.set(cpx_event.name, True, cpx_event.duration)

    def __str__(self):
        return self.name


class BaseSensor(models.Model):
    MEASURE_CHOICES = (
        ('S', 'Scalar'),
        ('B', 'Binary'),
        ('T', 'Text'),
        ('M', 'Misc'),
        ('C', 'Coord'),
        # Multimedia data to go
    )
    sn = models.ForeignKey('SensorNetwork', on_delete=models.CASCADE)
    iri = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=25)
    measure_type = models.CharField(choices=MEASURE_CHOICES, max_length=6)
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    is_moveable = models.BooleanField(default=False)

    def validate_input(self, sensor_input):
        """
        Sends input to validate with events.
        So far validates only scalar values (integer),and text.
        """
        result = []
        events = self.event_set.all(is_complex=False)
        for event in events:
            if hasattr(event, 'complexevent'):
                event = event.complexevent
            else:
                event = event.atomicevent

            if event.validate(sensor_input):
                result.append(event)

        return result

    def get_measure_type(self):
        return self.measure_type

    def get_location(self):
        return self.location

    def is_multimedia(self):
        return False

    def get_measure(self):
        return 'base'

    def __str__(self):
        return self.name


class Sensor(BaseSensor):
    def get_measure(self):
        return 'sensor'


class MultimediaSensor(BaseSensor):
    def get_measure(self):
        return 'multi'

    def is_multimedia(self):
        return True


class MeasureLog(TimeStampedModel):
    sensor = models.ForeignKey(
        BaseSensor,
        on_delete=models.CASCADE,
        related_name='measure_log'
    )
    # interest = models.BooleanField(default=False)
    value = models.CharField(max_length=100)

    def get_coordinates(self):
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


class Event(TimeStampedModel):
    sn = models.ForeignKey('SensorNetwork', on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    duration = models.IntegerField(blank=True)
    is_complex = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sn', 'name')

    def __str__(self):
        return self.name

    def add_to_queue(self):
        cache.set(str(self.name) + '_seq', True, ttl=self.duration + 5)
        cache.set(str(self.name), True, ttl=self.duration)
        return True

    def check_queue(self):
        return cache.get(str(self.name))

class AtomicEvent(Event):
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
        "true"
    )

    cause = models.ForeignKey(
        'BaseSensor',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='cause_sensor'
    )
    measure_limit = models.IntegerField(null=True, blank=True)
    function = models.CharField(
        max_length=25,
        choices=FUNCTIONS,
        default=FUNCTIONS.less_than
    )
    sensors = models.ManyToManyField('BaseSensor', blank=True)

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

    def true(self, op1, op2):
        return True

    def get_function(self):
        try:
            function = getattr(self, self.function)
            return function
        except Exception as e:
            raise e

    def get_function_name(self):
        return self.function

    def validate(self, sensor_input):
        """
        Applies designated event function to the value given
        by the sensor and the measure_limit.
        """
        function = self.get_function()
        result = function(sensor_input, self.measure_limit)

        return result


class ComplexEvent(Event):
    OPERATORS = Choices(
        "seq",
        "overlaps",
        "any"
    )

    first_event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name="first_ev"
    )
    second_event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name="second_ev"
    )
    function = models.CharField(
        max_length=10,
        choices=OPERATORS,
        default=OPERATORS.seq
    )

    def save(self, *args, **kwargs):
        self.is_complex = True
        return super(ComplexEvent ,self).save(*args, **kwargs)

    def is_happening(self):
        if self.function == self.OPERATORS.overlaps:
            if cache.get(self.first_event.name) and cache.get(self.second_event.name):
                return True
        elif self.function == self.OPERATORS.seq or self.OPERATORS.any:
            if cache.get(self.first_event.name + '_seq') and cache.get(self.second_event.name + '_seq'):
                return True
        return False
