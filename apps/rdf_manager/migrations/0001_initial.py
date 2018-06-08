# Generated by Django 2.0.5 on 2018-06-01 01:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NameSpace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('uri', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='OntoFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Ontology',
            fields=[
                ('namespace_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='rdf_manager.NameSpace')),
                ('loaded_graph', models.BooleanField(default=False)),
                ('loaded_ontologies', models.IntegerField(default=0)),
                ('loaded_namespaces', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Ontologies',
            },
            bases=('rdf_manager.namespace',),
        ),
        migrations.AlterUniqueTogether(
            name='namespace',
            unique_together={('name', 'uri')},
        ),
        migrations.AddField(
            model_name='ontology',
            name='namespaces',
            field=models.ManyToManyField(blank=True, related_name='ontology_namespaces', to='rdf_manager.NameSpace'),
        ),
        migrations.AddField(
            model_name='ontology',
            name='ontology_files',
            field=models.ManyToManyField(blank=True, to='rdf_manager.OntoFile'),
        ),
    ]
