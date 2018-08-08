import json

from django.shortcuts import render
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View, CreateView, FormView, ListView, UpdateView, TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import SensorNetwork, BaseSensor, MeasureLog, AtomicEvent, Event


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
        self.sensor = get_object_or_404(
            BaseSensor,
            iri=self.kwargs.get('sensor_iri')
        )
        return super(SensorPipeline, self).dispatch(request, *args, **kwargs)

    # All the secure request and that not ready
    def get(self, request, sn_id, sensor_iri):
        measures = self.sensor.measure_log

        response = {
            'measures': list(measures.values_list("value", flat=True)),
        }
        if measures:
            return JsonResponse(data=response, status=200)
        else:
            return JsonResponse(data=response, status=204)

    def post(self, request, sn_id, sensor_iri):
        measure = ''
        if self.sensor.measure_type == 'C':
            measure = request.POST.get('lat') + ',' + request.POST.get('lon')
        else:
            measure += request.POST.get('measure')

        measure = MeasureLog(
            sensor=self.sensor,
            value=measure,
        )

        if hasattr(self.sensor, 'multimediasensor'):
            self.sensor = self.sensor.multimediasensor
        else:
            self.sensor = self.sensor.sensor


        # Here it checks if any atomic event condition is met by this measure
        validate = self.sensor.validate_input(
            measure.get_value()
        )

        location = self.sensor.sn.get_location(sensor=self.sensor, measure=measure)
        if location:
            location = str(location[0][0])
        else:
            location = ''

        response = {
            'response':'location: ' + location
        }

        if validate:
            measure.save()
            response['response'] += ". Ocurrio evento: "
            for event in validate:
                event.add_to_queue()
                response['response'] += event.name + ', '

            complex_events = self.sensor.sn.update_complex_queue()
        else:
            response['response'] += ". No ocurrio evento."
            complex_events = self.sensor.sn.check_complex_queue()

        response['response'] += 'Complex: ' + str([e.name for e in complex_events])
        return JsonResponse(
            data=response,
            status=200
        )


class SensorStimulusView(TemplateView):
    template_name = 'sensor-result.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        event = self.kwargs['event_iri']
        value = self.kwargs['value']

        atomic_event = get_object_or_404(AtomicEvent, pk=event)
        result = atomic_event.validate(int(value))

        context['result'] = result

        return self.render_to_response(context)


class SensorNetworkComplexEvents(TemplateView):
    def post(self, request, sn_id):
        # Add some sort of cache here
        sn = get_object_or_404(SensorNetwork, id=sn_id)
        complex_events = sn.update_complex_queue()
        return JsonResponse(
            data=serialize('json', complex_events, fields={'name'}),
            status=200
        )