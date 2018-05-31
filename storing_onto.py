import rdflib
import psycopg2
import rdflib_sqlalchemy

from rdflib.graph import ConjunctiveGraph as Graph
from rdflib import plugin
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib.namespace import Namespace
from rdflib.term import Literal
from rdflib.term import URIRef

em_onto = Namespace('http://webprotege.stanford.edu/')
db_type = 'PostgreSQL'
onto_file = '/home/edgar/Tesis/django-onto/django_mssn/912-onto-ontologies/912-onto/root-ontology.owl'
dburi = rdflib.URIRef('postgres+psycopg2://rdfuser:rdfpass@localhost/rdflibonto')

rdflib_sqlalchemy.registerplugins()

ident = em_onto.rdfgraph
store = plugin.get('SQLAlchemy', Store)(identifier=ident)

# Open previously created store, or create it if it doesn't exist yet.
graph = Graph(store, ident)

rt = graph.open(dburi, create=True)
if rt == NO_STORE:
    # There is no underlying Sleepycat infrastructure, create it
    graph.open(dburi, create=True)
else:
    assert rt == VALID_STORE, "The underlying store is corrupt"

print("Triples in graph before parse: ", len(graph))

ssn_namespace = Namespace('http://www.w3.org/ns/ssn/')
sosa_namespace = Namespace('http://www.w3.org/ns/sosa/')
mssn_namespace = Namespace('http://mssn.sigappfr.org/mssn/')

graph.bind('ssn', ssn_namespace)
graph.bind('sosa', sosa_namespace)
graph.bind('mssn', mssn_namespace)

graph.parse(onto_file)
graph.commit()

print("Triples in graph after parse: ", len(graph))

# display the graph in RDF/XML
print(graph.serialize())

graph.close()