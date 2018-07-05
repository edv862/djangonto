from django.urls import re_path

from .views import SNDetails, SensorPipeline, SNList

app_name = 'rdf_manager'
urlpatterns = [
    re_path(r'^$', SNList.as_view(), name='sn_list'),
    re_path(r'^<sn_id>/$', SNDetails.as_view(), name='sn_details'),
    re_path(r'^<sn_id>/<sensor_iri>/$', SensorPipeline.as_view(), name='sensor_pipeline'),
]
