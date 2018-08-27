from django.urls import re_path

from .views import SNDetails, SensorPipeline, SNList, SensorStimulusView, PlatformComplexEvents

app_name = 'rdf_manager'
urlpatterns = [
    re_path(r'^$', SNList.as_view(), name='sn_list'),
    re_path(r'^(?P<sn_id>\w+)/$', SNDetails.as_view(), name='sn_details'),
    re_path(
        r'^(?P<sn_id>\w+)/(?P<sensor_iri>\w+)/$',
        SensorPipeline.as_view(),
        name='sensor_pipeline'
    ),
    re_path(
        r'^event/(?P<event_iri>\w+)/(?P<value>\w+)/$',
        SensorStimulusView.as_view(),
        name='sensor_pipeline'
    ),
    re_path(
        r'^(?P<sn_id>\w+)/complex_events/$',
        PlatformComplexEvents.as_view(),
        name='complex_events'
    ),
]
