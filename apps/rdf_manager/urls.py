from django.urls import path
from .views import load_graph

app_name = 'rdf_manager'
urlpatterns = [
    path(r'', load_graph, name='test'),
]
