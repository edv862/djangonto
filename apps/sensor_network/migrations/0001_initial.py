# Generated by Django 2.0.5 on 2018-07-25 00:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseSensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iri', models.CharField(max_length=25, unique=True)),
                ('name', models.CharField(max_length=25)),
                ('measure_type', models.CharField(choices=[('S', 'Scalar'), ('B', 'Binary'), ('T', 'Text'), ('M', 'Misc'), ('C', 'Coord')], max_length=6)),
                ('is_moveable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=25)),
                ('duration', models.IntegerField(blank=True)),
                ('is_complex', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('coordinates', models.CharField(blank=True, max_length=40)),
                ('extra_info', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='LocationMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('locations', models.ManyToManyField(blank=True, to='sensor_network.Location')),
            ],
        ),
        migrations.CreateModel(
            name='MeasureLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('value', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SensorNetwork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('location_map', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sensor_network.LocationMap')),
            ],
        ),
        migrations.CreateModel(
            name='AtomicEvent',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sensor_network.Event')),
                ('measure_limit', models.IntegerField(blank=True, null=True)),
                ('function', models.CharField(choices=[('less_than', 'less_than'), ('great_than', 'great_than'), ('less_than_equal', 'less_than_equal'), ('great_than_equal', 'great_than_equal'), ('not_less_than', 'not_less_than'), ('not_great_than', 'not_great_than'), ('not_less_than_equal', 'not_less_than_equal'), ('not_great_than_equal', 'not_great_than_equal'), ('equal', 'equal'), ('not_equal', 'not_equal'), ('true', 'true')], default='less_than', max_length=25)),
            ],
            options={
                'abstract': False,
            },
            bases=('sensor_network.event',),
        ),
        migrations.CreateModel(
            name='ComplexEvent',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sensor_network.Event')),
                ('function', models.CharField(choices=[('seq', 'seq'), ('seq_anyoverlaps', 'seq_anyoverlaps'), ('any', 'any')], default='seq', max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('sensor_network.event',),
        ),
        migrations.CreateModel(
            name='MultimediaSensor',
            fields=[
                ('basesensor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sensor_network.BaseSensor')),
            ],
            bases=('sensor_network.basesensor',),
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('basesensor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sensor_network.BaseSensor')),
            ],
            bases=('sensor_network.basesensor',),
        ),
        migrations.AddField(
            model_name='measurelog',
            name='sensor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='measure_log', to='sensor_network.BaseSensor'),
        ),
        migrations.AddField(
            model_name='event',
            name='sn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensor_network.SensorNetwork'),
        ),
        migrations.AddField(
            model_name='basesensor',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sensor_network.Location'),
        ),
        migrations.AddField(
            model_name='basesensor',
            name='sn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensor_network.SensorNetwork'),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together={('sn', 'name')},
        ),
        migrations.AddField(
            model_name='complexevent',
            name='first_event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='first_ev', to='sensor_network.Event'),
        ),
        migrations.AddField(
            model_name='complexevent',
            name='second_event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='second_ev', to='sensor_network.Event'),
        ),
        migrations.AddField(
            model_name='atomicevent',
            name='cause',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cause_sensor', to='sensor_network.BaseSensor'),
        ),
        migrations.AddField(
            model_name='atomicevent',
            name='sensors',
            field=models.ManyToManyField(blank=True, to='sensor_network.BaseSensor'),
        ),
    ]
