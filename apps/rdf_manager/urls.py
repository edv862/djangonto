from django.conf.urls import url
from django.urls import path
from .views import load_graph, load_hardcoded_onto, load_hardcoded_onto_1

app_name = 'rdf_manager'
urlpatterns = [
    url(r'cable/$', load_hardcoded_onto),
    url(r'cable1/$', load_hardcoded_onto_1),
    path(r'', load_graph, name='test'),
]
