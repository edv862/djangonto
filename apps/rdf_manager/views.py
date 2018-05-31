from django.shortcuts import render
from django.http import HttpResponse
from .models import Ontology

def load_graph(request):
	g = Ontology.objects.all()[0].load_graph().serialize(format='n3').decode('utf')
	return render(request, 'graph.html', {'graph': g})
