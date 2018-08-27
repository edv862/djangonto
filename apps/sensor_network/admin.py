from django.contrib import admin

from .models import *

admin.site.register(AtomicEvent)
admin.site.register(ComplexEvent)

admin.site.register(LocationMap)
admin.site.register(Location)

admin.site.register(MultimediaSensor)
admin.site.register(Platform)
admin.site.register(Sensor)
