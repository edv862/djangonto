from django.conf.urls import url

from .views import load_hardcoded_onto

urlpatterns = [
    url(r'cable/$', load_hardcoded_onto),
]
