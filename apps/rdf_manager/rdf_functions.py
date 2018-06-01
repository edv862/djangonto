import rdflib_sqlalchemy

from rdflib import plugin
from rdflib.graph import ConjunctiveGraph as Graph
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib.term import Literal, URIRef
from rdflib.namespace import Namespace, NamespaceManager

# TODO: method that from a namespace gives you a graph with the ontology.
# So you can have several ontologies in the same db.

class GraphOntology():
    db_type = ['PostgreSQL'] # TODO: add more bd support.
    onto_namespace = None
    database_uri = None

    graph = None
    # Namespaces must be a tuple with ('Name', URI).
    # As Graph.bind method.
    namespaces = []

    def __init__(
        self, namespace, db_user, db_password, db_name,
        db_type='PostgreSQL', db_host='localhost', onto_file=None
    ):
        '''
        Args:
            namespace, to identify graph.
            db_type, to use with django database, defaults postgres.
            onto_file, in rdf format to load graph with data. (Optional)
            db_user.
            db_password.
            db_name.
            db_host.
        '''
        
        # Registering plugins for database supports.
        rdflib_sqlalchemy.registerplugins()

        onto_namespace = Namespace(namespace)
        ident = onto_namespace.rdfgraph
        store = plugin.get('SQLAlchemy', Store)(identifier=ident)
        self.graph = Graph(store, ident)

        try:
            uri = 'postgres+psycopg2://'+db_user+':'+db_password+'@'+db_host+'/'+db_name
            db_uri = URIRef(uri)

            # Open database to store graph.
            rt = self.graph.open(db_uri, create=True)

            # Check if database is ok.
            assert rt == VALID_STORE, "The underlying store is corrupt"

            print("Graph created correctly.")
        except Exception as e:
            # Restore graph None value.
            self.graph = None
            print(e)

        if onto_file is not None:
            try:
                self.graph.parse(onto_file)
                self.graph.commit()
                print("Triples added to graph: ", len(self.graph))
            except Exception as e:
                print("There was an error: "+str(e))

    def add_namespace(self, name, uri):
        '''
        Graph.bind abstraction.
        '''
        new_namespace = Namespace(uri)
        self.graph.bind(name, new_namespace)
        self.graph.commit()
        print("Namespace added to graph.")

    def load_triples_from_file(self, file_name):
        '''
        Graph.parse abstraction.
        '''
        try:
            self.graph.parse(file_name)
            self.graph.commit()
            print("Triples added to graph: ", len(self.graph))
        except Exception as e:
            print("There was an error: ", str(e))

    def serialize(self, format):
        return self.graph.serialize(format=format)

    def close(self):
        self.graph.close()
