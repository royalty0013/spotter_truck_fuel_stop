# Generated by Django 3.2.23 on 2025-06-22 18:14

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FuelStop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opis_truckstop', models.IntegerField()),
                ('truckstop_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=50)),
                ('rack_id', models.IntegerField()),
                ('retail_price', models.DecimalField(decimal_places=3, max_digits=10)),
                ('point', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
            ],
        ),
    ]
