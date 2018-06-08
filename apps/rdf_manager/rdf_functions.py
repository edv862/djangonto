import rdflib_sqlalchemy

from rdflib import plugin, URIRef
from rdflib.graph import ConjunctiveGraph as Graph
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib.term import Literal, URIRef
from rdflib.namespace import Namespace, NamespaceManager

# TODO: method that from a namespace gives you a graph with the ontology.
# So you can have several ontologies in the same db.

class GraphOntology():
    db_type = ['PostgreSQL'] # TODO: add more bd support.
    onto_uri = None
    database_uri = None

    graph = None
    # Namespaces must be a tuple with ('Name', URI).
    # As Graph.bind method.
    namespaces = []

    def __init__(
        self, namespace, db_user, db_password, db_name, create=True,
        db_type='PostgreSQL', db_host='localhost', db_port='5432', onto_file=None
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

        onto_uri = URIRef(namespace)
        store = plugin.get('SQLAlchemy', Store)(identifier=onto_uri)
        self.graph = Graph(store, onto_uri)
        try:
            uri = 'postgres+psycopg2://'+db_user+':'+db_password+'@'+db_host+':' + db_port + '/'+db_name
            db_uri = URIRef(uri)

            # Open database to store graph.
            rt = self.graph.open(db_uri, create=create)
            # Check if database is ok.
            assert rt == VALID_STORE, "The underlying store is corrupt"

            if create:
                print("Graph created correctly.")
            else:
                print("Graph loaded correctly.")
        
        except Exception as e:
            # Restore graph None value.
            self.graph = None
            print(e)

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

    def destroy(self):
        self.graph.destroy(self.onto_uri)
        try:
            self.graph.close()
        except:
            pass
