from django.contrib import admin

from .models import NameSpace, Ontology, OntoFile

admin.site.register(NameSpace)
admin.site.register(Ontology)
admin.site.register(OntoFile)
