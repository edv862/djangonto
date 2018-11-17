import functools
import math
import numpy as np

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from django.core.cache import cache
from django.db import models

from model_utils import Choices
from model_utils.models import TimeStampedModel


class LocationMap(models.Model):
    name = models.CharField(max_length=25)
    locations = models.ManyToManyField('Location', blank=True)

    def __str__(self):
        return self.name

    def location_contains_point(self, vertices, point):
        # Check if a coordinate is inside a location
        if vertices and point:
            vertices[0].append(vertices[0][0])
            vertices[1].append(vertices[1][0])

            # # print(point)

            lons_lats_vect = np.column_stack((vertices[0], vertices[1])) # Reshape coordinates
            polygon = Polygon(lons_lats_vect) # create polygon
            p_point = Point(point[0], point[1]) # create point

            # # print(polygon.contains(p_point)) # check if polygon contains point
            # # print(p_point.within(polygon)) # check if a point is in the polygon

            return (p_point.within(polygon) or polygon.contains(p_point))
        else:
            return None

    def get_location(self, sensor=None, measure=None):
        in_location = False
        if sensor.is_moveable:
            if sensor and measure:
                point = measure.get_coordinates()
            elif sensor and not measure:
                    measure = MeasureLog.objects.filter(sensor=sensor).first()
                    if measure:
                        point = measure.get_coordinates()
                    else:
                        return None
            elif measure:
                point = measure.get_coordinates()
        else:
            if sensor.location:
                return sensor.location
            else:
                return None

        loc = None
        for location in self.locations.all():
            if location.get_vertices:
                in_location = self.location_contains_point(location.get_vertices(), point)

            if in_location:
                loc = location
                break

        return loc


class Location(models.Model):
    name = models.CharField(max_length=25)

    point_1 = models.CharField(blank=True, max_length=25)
    point_2 = models.CharField(blank=True, max_length=25)
    point_3 = models.CharField(blank=True, max_length=25)
    point_4 = models.CharField(blank=True, max_length=25)
    point_5 = models.CharField(max_length=25, blank=True, null=True)
    point_6 = models.CharField(max_length=25, blank=True, null=True)

    extra_info = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    def get_vertices(self):
        """
        Returns value as tuple (lat,lon).
        """
        if self.point_1:
            lon = [
                self.get_coordinates(self.point_1)[0],
                self.get_coordinates(self.point_2)[0],
                self.get_coordinates(self.point_3)[0],
                self.get_coordinates(self.point_4)[0]
            ]

            lat = [
                self.get_coordinates(self.point_1)[1],
                self.get_coordinates(self.point_2)[1],
                self.get_coordinates(self.point_3)[1],
                self.get_coordinates(self.point_4)[1]
            ]

            if self.point_6 is not None:
                lon.append(self.get_coordinates(self.point_5)[0])
                lon.append(self.get_coordinates(self.point_6)[0])
                lat.append(self.get_coordinates(self.point_5)[1])
                lat.append(self.get_coordinates(self.point_6)[1])
            if self.point_6 is None:
                if self.point_5 is not None:
                    lon.append(self.get_coordinates(self.point_5)[0])
                    lat.append(self.get_coordinates(self.point_5)[1])

            return [lon, lat]
        else:
            return None

    def get_coordinates(self, point):
        if point == "":
            return (0, 0)
        aux = point.replace(" ", "").split(',')
        lat = float(aux[0])
        lon = float(aux[1])
        #return (lat, lon)
        return [lon, lat]


class SensorNetwork(models.Model):
    name = models.CharField(max_length=25)
    location_map = models.ForeignKey(
        'LocationMap',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def get_location(self, sensor=None, measure=None):
        return self.location_map.get_location(sensor=sensor, measure=measure)

    def check_complex_queue(self):
        l = []
        for cpx_event in self.event_set.filter(is_complex=True):
            if cache.get(cpx_event.name):
                l.append(cpx_event)
        return l

    def update_complex_queue(self):
        l = []
        for cpx_event in self.event_set.filter(is_complex=True):
            if cpx_event.complexevent.is_happening():
                cache.set(cpx_event.name + '_seq', True, cpx_event.duration + 8)
                cache.set(cpx_event.name, True, cpx_event.duration)
                l.append(cpx_event)
        return l

    def __str__(self):
        return self.name


class BaseSensor(models.Model):
    MEASURE_CHOICES = (
        ('S', 'Scalar'),
        ('B', 'Binary'),
        ('T', 'Text'),
        ('M', 'Misc'),
        ('Mu', 'Multi'),
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
        events = self.cause_sensor.all()
        for event in events:
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
        # print(self.value)
        aux = self.value.replace(" ", "").split(',')
        if len(aux) > 1:
            lat = float(aux[0])
            lon = float(aux[1])
            # return (lat, lon)
            return [lon, lat]
        else:
            return None

    def integer(self):
        """
        Returns value as integer
        """
        return int(self.value)

    def get_value(self):
        if self.sensor.get_measure_type() == 'C':
            return self.get_coordinates()
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
        cache.set(str(self.name) + '_seq', True, timeout=self.duration + 8)
        cache.set(str(self.name), True, timeout=self.duration)
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
        return function(sensor_input, self.measure_limit)


class ComplexEvent(Event):
    OPERATORS = Choices(
        "seq",
        "seq_any",
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
        # Check if any complex event its happening
        if not cache.get(self.first_event.name):
            if self.first_event.is_complex:
                if self.first_event.complexevent.is_happening():
                    cache.set(str(self.first_event.name) + '_seq', True, timeout=self.duration + 8)
                    cache.set(str(self.first_event.name), True, timeout=self.duration)


        if not cache.get(self.second_event.name):
            if self.second_event.is_complex:
                if self.second_event.complexevent.is_happening():
                    cache.set(str(self.second_event.name) + '_seq', True, timeout=self.duration + 8)
                    cache.set(str(self.second_event.name), True, timeout=self.duration)

        if self.function == self.OPERATORS.overlaps:
            return cache.get(self.first_event.name) and cache.get(self.second_event.name)
        elif self.function == self.OPERATORS.seq:
            return cache.get(self.first_event.name + '_seq') and cache.get(self.second_event.name)
        elif self.function == self.OPERATORS.seq_any:
            return (
                cache.get(self.first_event.name + '_seq') and cache.get(self.second_event.name) or
                cache.get(self.first_event.name) and cache.get(self.second_event.name + '_seq')
            )
        elif self.function == self.OPERATORS.any:
            return cache.get(self.first_event.name + '_seq') and cache.get(self.second_event.name + '_seq')
        return False


class EventAction(models.Model):
    FUNCTIONS = Choices(
        "true"
    )

    name = models.CharField(max_length=25)
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
    )
    iri = models.CharField(max_length=50)
    function = models.CharField(
        max_length=25,
        choices=FUNCTIONS,
        default=FUNCTIONS.true
    )

    def get_function(self):
        try:
            function = getattr(self, self.function)
            return function
        except Exception as e:
            raise e

    def true(self, op1, op2):
        return True

    def get_function_name(self):
        return self.function

    def execute(self):
        """
        Applies designated event function to the value given
        by the sensor and the measure_limit.
        """
        function = self.get_function()
        return function()
