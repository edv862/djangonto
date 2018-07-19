# Generated by Django 2.0.5 on 2018-07-17 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sensor_network', '0005_merge_20180705_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='iri',
            field=models.CharField(default='gabo-phone', max_length=25),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='atomicevent',
            name='cause',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='sensor_network.Sensor'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='measure_type',
            field=models.CharField(choices=[('S', 'Scalar'), ('B', 'Binary'), ('T', 'Text'), ('M', 'Misc'), ('C', 'Coord')], max_length=6),
        ),
    ]