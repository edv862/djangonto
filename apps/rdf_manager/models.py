import json
from django.db import models
from django.conf import settings

from rdflib import Graph

from .ref_definitions import *
from .rdf_functions import GraphOntology


class NameSpace(models.Model):
    name = models.CharField(max_length=30)
    uri = models.CharField(max_length=50)

    class Meta:
        unique_together = ('name', 'uri')

    def __str__(self):
        return self.name


class Ontology(models.Model):
    namespaces = models.ManyToManyField(
        'Namespace',
        related_name='ontology_namespaces',
        blank=True,
    )
    ontology_files = models.ManyToManyField(
        'OntoFile',
    )
    loaded_graph = models.BooleanField(default=False)
    loaded_ontologies = models.IntegerField(default=0)
    loaded_namespaces = models.IntegerField(default=0)

    def load_graph(self):
        # Create and load Graph from file
        # graph = rdflib.Graph()

        # Create dbtables to save the Graph
        graph = GraphOntology(
            namespace=self.uri, create=True,
            db_user=settings.DATABASES['default']['USER'],
            db_password=settings.DATABASES['default']['PASSWORD'],
            db_name=settings.DATABASES['default']['NAME'],
            db_host=settings.DATABASES['default']['HOST']
        )

        # Load All the Ontologies files
        for f in self.ontology_files.all():
            # graph.parse(f.file.url[1:])
            graph.load_triples_from_file(
                file_name=f.file.url[1:]
            )

        # Bind the ontologies Namespaces to the Ontologies on the Graph
        self.bind_namespaces(graph)

        if not self.loaded_graph:
            self.loaded_graph = True
            self.save()

        return graph

    def bind_namespaces(self, graph):
        for namespace in self.namespaces.all():
            # Define & Bind custom ontologies namespaces to the graph
            graph.add_namespace(
                name=namespace.name,
                uri=namespace.uri,
            )
        return graph

    def get_graph(self):
        graph = GraphOntology(
            namespace=self.uri, create=False,
            db_user=settings.DATABASES['default']['USER'],
            db_password=settings.DATABASES['default']['PASSWORD'],
            db_name=settings.DATABASES['default']['NAME'],
            db_host=settings.DATABASES['default']['HOST'],
        )

        return graph

    # Functions to load an ontology into the system from a rdf file.
    def open_file(self):
        g = Graph()
        g.parse(ONTO_FILE)

        return g

    def str_to_class(self, class_str):
        import apps.sensor_network.models as sn_model

        # TODO: Make separate model for MobileSensor?.
        if class_str.__str__() == "MobileSensor":
            class_str = "Sensor"

        try:
            model = sn_model.__dict__[class_str.__str__()]
            return model
        except Exception as e:
            # print(e)
            raise(e)

    def get_classes(self):
        g = self.open_file()
        classes = []

        # for graphg in g.triples((None, None, None)):
        #     print(graphg)

        try:
            classes_ref = g.triples((None, None, IS_CLASS))
            for class_ref in classes_ref:
                reference = class_ref[0]
                class_label = g.label(reference)
                try:
                    # Make that string a class
                    model_class = self.str_to_class(class_label)
                    # Get Individuals for that class.
                    individuals = self.get_individuals(
                        g,
                        reference,
                        model_class
                    )

                except Exception as e:
                    # print(e)
                    pass
        except Exception as e:
            raise e

        return classes

    def get_individuals(self, graph, reference, model):
        individuals = []

        try:
            for g in graph.triples((None, IS_TYPE, reference)):
                type_ref = g[0]
                instance = model()
                instance.name = graph.label(type_ref).__str__()
        except Exception as e:
            print(e)

        return individuals

    def prueba_json(self):
        g = self.open_file()

        json_b = g.serialize(format='json-ld', indent=4)

        # Decode UTF-8 bytes to Unicode, and convert single quotes
        # to double quotes to make it valid JSON
        json_graph = json_b.decode('utf8').replace("'", '"')

        # Load the JSON to a Python list & dump it back out as formatted JSON
        data = json.loads(json_graph)
        s = json.dumps(data, indent=4, sort_keys=True)
        print(s)

    def save(self):
        self.get_classes()

    class Meta:
        verbose_name_plural = "Ontologies"


class OntoFile(models.Model):
    file = models.FileField()

    def __str__(self):
        return self.file.url
