from django.db import models


class NameSpace(models.Model):
	name = models.CharField(max_length=30)
	uri = models.CharField(max_length=50)

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

	class Meta:
		verbose_name_plural = "Ontologies"


class OntoFile(models.Model):
	file = models.FileField()
