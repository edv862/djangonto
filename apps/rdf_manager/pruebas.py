import apps.sensor_network.models as models
from rdflib import Graph, URIRef, Literal, RDFS

ONTO_FILE = '/home/edgar/Tesis/django-onto/django_mssn/mssn-lite.owl'

IS_TYPE = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
IS_LABEL = URIRef('http://www.w3.org/2000/01/rdf-schema#label')
IS_CLASS = URIRef('http://www.w3.org/2002/07/owl#Class')

THING = URIRef('http://www.w3.org/2002/07/owl#Thing')


def str_to_class(str):
    for x in models.__dict__:
        print(x)


def prueba():
    g = Graph()
    g.parse('/home/edgar/Tesis/django-onto/django_mssn/mssn-lite.owl')

    try:
        classes = []
        classes_ref = g.triples((None, None, IS_CLASS))
        for class_ref in classes_ref:
            reference = class_ref[0]
            class_label = g.label(reference)

            print(class_label)
            try:
                # Make that string a class
                print("str_to_class(class_label)")
                print(str_to_class(class_label))
            except Exception as e:
                print(e)
    except Exception as e:
        raise e
