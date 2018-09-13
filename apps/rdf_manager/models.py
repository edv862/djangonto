import rdflib
from django.db import models
from django.conf import settings
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
        g.parse('/home/edgar/Tesis/django-onto/django_mssn/mssn-lite.owl')
        return g

    def get_classes(self):
        g = open_file()
        try:
            classes = []
            classes_ref = g.triples((None, None, IS_CLASS))
            for class_ref in classes_ref:
                reference = class_ref[0]
                class_label = g.label(reference)
                print(class_label)
        except Exception as e:
            raise e

    class Meta:
        verbose_name_plural = "Ontologies"


class OntoFile(models.Model):
    file = models.FileField()

    def __str__(self):
        return self.file.url
