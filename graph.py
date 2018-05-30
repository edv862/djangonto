import rdflib
from rdflib.namespace import Namespace, NamespaceManager

import pprint

graph = rdflib.Graph()

graph.parse('/home/edgar/Tesis/django-onto/django_mssn/912-onto-ontologies/912-onto/root-ontology.owl', formar='owl')

# aux = graph.subject_objects(
# 	predicate=rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label')
# )

# print(dict(aux))

ssn_namespace = Namespace('http://www.w3.org/ns/ssn/')
sosa_namespace = Namespace('http://www.w3.org/ns/sosa/')
mssn_namespace = Namespace('http://mssn.sigappfr.org/mssn/')
emergency_namespace = Namespace('http://webprotege.stanford.edu/')

graph.bind('ssn', ssn_namespace)
graph.bind('sosa', sosa_namespace)
graph.bind('mssn', mssn_namespace)
graph.bind('911-onto', emergency_namespace)

all_ns = [n for n in graph.namespace_manager.namespaces()]

# for x in all_ns:
# 	print(x)

aux = graph.value(
	subject=rdflib.term.URIRef('http://webprotege.stanford.edu/RDWcD1WossrmXH0BeGQAE8d'),
	predicate=rdflib.term.URIRef('http://mssn.sigappfr.org/mssn/above'),
)

# print(graph.namespace_manager.normalizeUri(aux))

# Normalizing data.
for x in graph.objects():
	try:
		print(graph.namespace_manager.normalizeUri(x))
	except:
		print("No se pudo normalizar.")
