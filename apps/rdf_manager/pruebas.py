import apps.sensor_network.models as models
from rdflib import Graph, URIRef, Literal, RDFS

ONTO_FILE = '/home/edgar/Tesis/django-onto/django_mssn/mssn-lite.owl'

IS_TYPE = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
IS_LABEL = URIRef('http://www.w3.org/2000/01/rdf-schema#label')
IS_CLASS = URIRef('http://www.w3.org/2002/07/owl#Class')

THING = URIRef('http://www.w3.org/2002/07/owl#Thing')


def str_to_class(class_str):
    try:
        model = models.__dict__[str(class_str)]
        return model
    except Exception as e:
        return None


def prueba():
    g = Graph()
    g.parse('/home/edgar/Tesis/django-onto/django_mssn/mssn-lite.owl')

    try:
        classes = []
        classes_ref = g.triples((None, None, IS_CLASS))
        for class_ref in classes_ref:
            reference = class_ref[0]
            class_label = g.label(reference)
            try:
                # Make that string a class
                model_class = str_to_class(class_label)
                print(class_label)
                print(model_class)
            except Exception as e:
                print(e)
    except Exception as e:
        raise e
