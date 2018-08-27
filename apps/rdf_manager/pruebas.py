from rdflib import Graph, URIRef, Literal, RDFS

is_type = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
is_label = URIRef('http://www.w3.org/2000/01/rdf-schema#label')

# location = URIRef('http://mssn.sigappfr.org/mssn/Location')
# location_map = URIRef('http://mssn.sigappfr.org/mssn/LocationMap')
g = Graph()
g.parse('/home/edgar/Tesis/django-onto/django_mssn/mssn-lite.owl')

# Gets location and location Map IRI.
try:
    location_map_triple = next(
        g.triples((None, is_label, Literal('LocationMap')))
    )
    location_map = URIRef(location_map_triple[0])
    location_triple = next(
        g.triples((None, is_label, Literal('Location')))
    )
    location = URIRef(location_triple[0])
except Exception as e:
    raise(e)

# Get location Maps.
# Returns an array just in case there are several location maps
# with the same name.
location_map_names = []
for triple in g.triples((None, is_type, location_map)):
    label = g.triples((triple[0], is_label, None))
    for names in label.__iter__():
        location_map_names += [names[2].__str__()]

print(location_map_names)


# Get locations.
# Returns an array just in case there are several locations
# with the same name.
location_names = []
for triple in g.triples((None, is_type, location)):
    label = g.triples((triple[0], is_label, None))
    for names in label.__iter__():
        location_names += [names[2].__str__()]

print(location_names)
