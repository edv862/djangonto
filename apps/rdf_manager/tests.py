from django.test import TestCase

# Create your tests here.

import apps.sensor_network.test_tools as tt
from apps.sensor_network.models import *

tt.send_concurrent_requests(SensorNetwork.objects.first())

