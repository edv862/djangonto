# Generated by Django 2.0.5 on 2018-07-25 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor_network', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complexevent',
            name='function',
            field=models.CharField(choices=[('seq', 'seq'), ('seq_anyoverlaps', 'seq_anyoverlaps'), ('any', 'any')], default='seq', max_length=10),
        ),
    ]
