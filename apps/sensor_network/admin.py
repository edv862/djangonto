from django.contrib import admin

from .models import *

admin.site.register(AtomicEvent)
admin.site.register(ComplexEvent)

admin.site.register(SensorNetwork)
admin.site.register(Sensor)
