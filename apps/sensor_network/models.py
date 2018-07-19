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
    location_map = models.ForeignKey(
        'LocationMap',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def get_location(self, sensor):
        return self

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
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    is_multimedia = models.BooleanField(default=False)
    is_moveable = models.BooleanField(default=False)

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

    def get_location(self):
        return self.location

    def __str__(self):
        return self.name

    def save(self, *args, first_save=True, **kwargs):
        if first_save:
            if self.is_multimedia:
                sensor = MultimediaSensor()
                for field in sensor._meta.fields:
                    if hasattr(sensor, field.name):
                        setattr(sensor, field.name, getattr(self, field.name))
                return super(MultimediaSensor, sensor).save(*args, first_save=False, **kwargs)
            elif self.is_moveable:
                sensor = MoveableSensor()
                for field in sensor._meta.fields:
                    if hasattr(sensor, field.name):
                        setattr(sensor, field.name, getattr(self, field.name))
                return super(MoveableSensor, sensor).save(*args, first_save=False, **kwargs)
            else:
                return super(Sensor, self).save(first_save=False)
        else:
            return super(Sensor, self).save(*args, first_save, **kwargs)

class MoveableSensor(Sensor):
    def save(self, *args, first_save=False, **kwargs):
        self.is_moveable = True
        return super(MoveableSensor, self).save(*args, first_save, **kwargs)


class MultimediaSensor(Sensor):
    def save(self, *args, first_save=False, **kwargs):
        self.is_multimedia = True
        return super(MultimediaSensor, self).save(*args, first_save, **kwargs)


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


class Event(TimeStampedModel):
    name = models.CharField(max_length=25)
    time_end = models.DateTimeField(blank=True)
    is_complex = models.BooleanField(default=False)

    def __str__(self):
        return self.name


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
    )

    cause = models.ForeignKey(
        'Sensor',
        on_delete=models.CASCADE,
        related_name='events'
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
        "Seq",
        "Overlaps",
        "Both"
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
        default=OPERATORS.Seq
    )

    def save(self, *args, **kwargs):
        self.is_complex = True
        return super(ComplexEvent ,self).save(*args, **kwargs)
