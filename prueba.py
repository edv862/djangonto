from owlready2 import *


ONTO_FILE = '/home/edgar/Tesis/django-onto/django_mssn/me-ssn.owl'
ONTO_FILE_912 = '/home/edgar/Tesis/django-onto/django_mssn/912.owl'
onto_path.append(ONTO_FILE)
onto = get_ontology()
onto.load()

print(onto)
