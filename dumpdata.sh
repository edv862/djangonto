python manage.py dumpdata --indent 2 auth.user -o fixture/users.json
python manage.py dumpdata --indent 2 rdf_manager -o fixture/ontologies.json
python manage.py dumpdata --indent 2 sensor_network -o fixture/ssn.json
