from django.conf.urls import url
from django.urls import path
from .views import load_graph, load_hardcoded_onto

app_name = 'rdf_manager'
urlpatterns = [
    url(r'cable/$', load_hardcoded_onto),
    path(r'', load_graph, name='test'),
]
