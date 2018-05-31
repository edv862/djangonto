from django.db import models
import rdflib
from rdflib.namespace import Namespace, NamespaceManager


class NameSpace(models.Model):
	name = models.CharField(max_length=30)
	uri = models.CharField(max_length=50)

	class Meta:
		unique_together = ('name', 'uri')

	def __str__(self):
		return self.name


class Ontology(NameSpace):
	namespaces = models.ManyToManyField(
		'Namespace',
		related_name='ontology_namespaces',
		blank=True,
	)
	ontology_files = models.ManyToManyField(
		'OntoFile',
		blank=True,
	)

	def load_graph(self):
		# Create and load Graph from file
		graph = rdflib.Graph()
		
		for f in self.ontology_files.all():
			graph.parse(f.file.url[1:])

		self.bind_namespaces(graph)

		return graph

	def bind_namespaces(self, graph):
		for namespace in self.namespaces.all():
			# Define & Bind custom ontologies namespaces to the graph
			nm = Namespace(namespace.uri)
			graph.bind(namespace.name, nm)
		
		return graph

	class Meta:
		verbose_name_plural = "Ontologies"


class OntoFile(models.Model):
	file = models.FileField()

	def __str__(self):
		return self.file.url
