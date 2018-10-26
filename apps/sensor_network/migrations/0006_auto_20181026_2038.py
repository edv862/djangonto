# Generated by Django 2.0.5 on 2018-10-26 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor_network', '0005_auto_20180918_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='point_5',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='point_6',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='basesensor',
            name='measure_type',
            field=models.CharField(choices=[('S', 'Scalar'), ('B', 'Binary'), ('T', 'Text'), ('M', 'Misc'), ('Mu', 'Multi'), ('C', 'Coord')], max_length=6),
        ),
    ]
