from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.views import View
from django.views.generic import CreateView, FormView, ListView, UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import SensorNetwork, Sensor, Measure


class SNList(LoginRequiredMixin, ListView):
    permission_required = 'is_staff'
    login_url = '/admin/login/'
    model = SensorNetwork
    template_name = 'sn_list.html'
    context_object_name = 'sns'


class SNDetails(LoginRequiredMixin, ListView):
    permission_required = 'is_staff'
    login_url = '/admin/login/'
    model = SensorNetwork
    template_name = 'sn_list.html'



@method_decorator(csrf_exempt, name='dispatch')
class SensorPipeline(View):
    def dispatch(self, request, *args, **kwargs):
        self.sensor = get_object_or_404(Sensor, id=sensor_iri)
        return super(SensorPipeline, self).dispatch(request, *args, **kwargs)

    # All the secure request and that not ready
    def get(request, sn_id, sensor_iri):
        measures = self.sensor.measures.all()
        if measures:
            return JsonResponse(measures.last(), status=200)
        else:
            return JsonResponse(status=204)

    def post(request, sn_id, sensor_iri):
        measure = {}
        for key in request.POST:
            if 'csrf' not in key:
                measure[key] = request.POST.get(key)

        measure = Measure(value=str(measure))
        measure.save()
        self.sensor.measures.add(measure)
        return HttpResponse(status=200)
