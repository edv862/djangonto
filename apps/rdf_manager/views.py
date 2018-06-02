from os import environ

from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from .models import Ontology

from .rdf_functions import GraphOntology

from django.conf import settings

def load_hardcoded_onto(request):
    graph = GraphOntology(
        namespace='http://dbpedia.org/',
        db_user=settings.DATABASES['default']['USER'],
        db_password=settings.DATABASES['default']['PASSWORD'],
        db_name=settings.DATABASES['default']['NAME'],
        db_host=settings.DATABASES['default']['HOST']
    )

    onto_file = '/home/edgar/Tesis/django-onto/django_mssn/912-onto-ontologies/912-onto/root-ontology.owl'

    # Adding namespaces
    graph.add_namespace(
        name='ssn',
        uri='http://www.w3.org/ns/ssn/',
    )
    graph.add_namespace(
        name='sosa',
        uri='http://www.w3.org/ns/sosa/',
    )
    graph.add_namespace(
        name='mssn',
        uri='http://mssn.sigappfr.org/mssn/',
    )

    # Load onto file.
    # graph.load_triples_from_file(
    #     file_name=onto_file
    # )

    return HttpResponse(graph.graph.serialize(format='n3'))

def load_graph(request):
    g = Ontology.objects.all()[0]
    if g:
        #if g.loaded_graph:
        #    g = g.get_graph()
        #else:
        g = g.load_graph()
        graph = g.serialize(format='n3').decode('utf')
        g.destroy()
    return render(request, 'graph.html', {'graph': graph})
