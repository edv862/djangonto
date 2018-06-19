from django.contrib import admin
from .models import NameSpace, Ontology, OntoFile


class OntologyAdmin(admin.ModelAdmin):
    filter_horizontal = ('namespaces', 'ontology_files')


admin.site.register(Ontology, OntologyAdmin)
admin.site.register(NameSpace)
admin.site.register(OntoFile)
