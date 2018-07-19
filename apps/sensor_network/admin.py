from django.contrib import admin

from .models import *

admin.site.register(Event)
admin.site.register(AtomicEvent)
admin.site.register(ComplexEvent)

admin.site.register(SensorNetwork)
admin.site.register(Sensor)
admin.site.register(MoveableSensor)
admin.site.register(MultimediaSensor)
