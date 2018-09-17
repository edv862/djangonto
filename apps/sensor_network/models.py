import math

from django.core.cache import cache
from django.db import models

from model_utils import Choices
from model_utils.models import TimeStampedModel

from apps.rdf_manager.models import Ontology


class Platform(models.Model):
    """
    Sensor Network has a reverse relation in Event model.
    ComplexEvent extends Event class.
    Platform can have an event list (event_set, from the reverse
    relation) and check if they are complex with is_complex
    field in Event.
    """
    name = models.CharField(max_length=25)
    ontology = models.ForeignKey(
        Ontology,
        related_name='sensor_network',
        on_delete=models.CASCADE
    )

    def get_location(self, sensor=None, measure=None):
        """ Returns sensor location on LocationMap. """
        return self.location_map.get_location(sensor=sensor, measure=measure)

    def check_complex_queue(self):
        """ Returns complex event list stored in cache queue. """
        cpx_event_list = []
        for cpx_event in self.event_set.filter(is_complex=True):
            if cache.get(cpx_event.name):
                cpx_event_list.append(cpx_event)
        return cpx_event_list

    def update_complex_queue(self):
        cpx_event_list = []

        for cpx_event in self.event_set.filter(is_complex=True):
            # Explicit call for validate from ComplexEvent.
            if cpx_event.complexevent.validate():
                # TODO: que co;o significa el +8
                cache.set(
                    cpx_event.name + '_seq',
                    True,
                    cpx_event.duration + 8
                )
                cache.set(cpx_event.name, True, cpx_event.duration)
                cpx_event_list.append(cpx_event)
        return cpx_event_list

    def __str__(self):
        return self.name


class LocationMap(models.Model):
    name = models.CharField(max_length=25)
    platform = models.ForeignKey(
        Platform,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='location_map'
    )

    def __str__(self):
        return self.name

    def get_location(self, sensor=None, measure=None):
        if sensor.is_moveable:
            if sensor and measure:
                measure = measure.get_coordinates()
            elif sensor and not measure:
                    measure = MeasureLog.objects.filter(sensor=sensor).first()
                    if measure:
                        measure = measure.get_coordinates()
                    else:
                        return None
            elif measure:
                measure = measure.get_coordinates()
        else:
            if sensor.location:
                return ([sensor.location], 0)
            else:
                return None

        loc = []
        min_dist = 0
        for location in self.location.all():
            coord1 = location.get_coordinates()
            distance = math.sqrt(
                math.pow(coord1[0] - measure[0], 2) +
                math.pow(coord1[1] - measure[1], 2)
            )
            if loc:
                if distance < min_dist:
                    loc = [location]
                    min_dist = distance
                elif distance == min_dist:
                    loc.append(location)
            else:
                loc = [location]
                min_dist = distance

        return (loc, min_dist)


class Location(models.Model):
    name = models.CharField(max_length=25)
    # Coord stored as  a string "lat, long".
    coordinates = models.CharField(max_length=40, blank=True)
    extra_info = models.CharField(max_length=100, blank=True)
    location_map = models.ForeignKey(
        LocationMap,
        on_delete=models.CASCADE,
        related_name='location'
    )

    def __str__(self):
        return self.name

    def get_coordinates(self):
        """
        Returns value as tuple (lat,lon).
        """
        aux = self.coordinates.replace(" ", "").split(',')
        lat = float(aux[0])
        lon = float(aux[1])
        return (lat, lon)


class Sensor(models.Model):
    MEASURE_CHOICES = (
        ('S', 'Scalar'),
        ('B', 'Binary'),
        ('T', 'Text'),
        ('M', 'Misc'),
        ('C', 'Coord'),
        # Multimedia data to go
    )
    sn = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE
    )
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
        events = self.atomicevent_set.all()
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


class MultimediaSensor(Sensor):
    def get_measure(self):
        return 'multi'

    def is_multimedia(self):
        return True


class MeasureLog(TimeStampedModel):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='measure_log'
    )
    # interest = models.BooleanField(default=False)
    value = models.CharField(max_length=100)

    def get_coordinates(self):
        """
        Returns value as tuple (lat,lon).
        """
        aux = self.value.replace(" ", "").split(',')
        lat = float(aux[0])
        lon = float(aux[1])
        return (lat, lon)

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
    sn = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=25)
    duration = models.IntegerField(default= 1, blank=True)
    is_complex = models.BooleanField(default=False)

    # TODO: Define actions on certain events.
    action = models.CharField(
        max_length=25,
        null=True,
        blank=True
    )

    # ComplexEvent is an instance of Event.
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
        Sensor,
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
        return super(ComplexEvent, self).save(*args, **kwargs)

    def validate(self):
        # Check if any complex event its happening
        if not cache.get(self.first_event.name):
            if self.first_event.is_complex:
                if self.first_event.complexevent.validate():
                    cache.set(
                        str(self.first_event.name) + '_seq',
                        True,
                        timeout=self.duration + 8
                    )
                    cache.set(
                        str(self.first_event.name),
                        True,
                        timeout=self.duration
                    )

        if not cache.get(self.second_event.name):
            if self.second_event.is_complex:
                if self.second_event.complexevent.validate():
                    cache.set(
                        str(self.second_event.name) + '_seq',
                        True,
                        timeout=self.duration + 8
                    )
                    cache.set(
                        str(self.second_event.name),
                        True,
                        timeout=self.duration
                    )

        if self.function == self.OPERATORS.overlaps:
            return (cache.get(self.first_event.name) and
                    cache.get(self.second_event.name))
        elif self.function == self.OPERATORS.seq:
            return (cache.get(self.first_event.name + '_seq') and
                    cache.get(self.second_event.name))
        elif self.function == self.OPERATORS.seq_any:
            return (
                cache.get(self.first_event.name + '_seq') and
                cache.get(self.second_event.name) or
                cache.get(self.first_event.name) and
                cache.get(self.second_event.name + '_seq')
            )
        elif self.function == self.OPERATORS.any:
            return (cache.get(self.first_event.name + '_seq') and
                    cache.get(self.second_event.name + '_seq'))
        return False
