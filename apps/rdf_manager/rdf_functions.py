import rdflib
from rdflib.namespace import Namespace, NamespaceManager

def load_graph(fname):
	# Create and load Graph from file
	graph = rdflib.Graph()
	graph.parse('912-onto-ontologies/912-onto/root-ontology.owl')

	# Define & Bind custom ontologies namespaces to the graph
	ssn_namespace = Namespace('http://www.w3.org/ns/ssn/')
	sosa_namespace = Namespace('http://www.w3.org/ns/sosa/')
	mssn_namespace = Namespace('http://mssn.sigappfr.org/mssn/')
	emergency_namespace = Namespace('http://webprotege.stanford.edu/')
	graph.bind('ssn', ssn_namespace)
	graph.bind('sosa', sosa_namespace)
	graph.bind('mssn', mssn_namespace)
	graph.bind('911-onto', emergency_namespace)
	return graph
	
	
