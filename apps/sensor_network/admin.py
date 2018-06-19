from django.contrib import admin

from .models import *

admin.site.register(Sensor)
admin.site.register(SensorNetwork)

admin.site.register(Location)
admin.site.register(LocationMap)
admin.site.register(Measure)

admin.site.register(Event)
admin.site.register(AtomicEvent)
admin.site.register(ComplexEvent)
