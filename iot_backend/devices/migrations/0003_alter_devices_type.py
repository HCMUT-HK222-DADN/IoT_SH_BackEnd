# Generated by Django 4.1.3 on 2023-04-03 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_alter_devices_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devices',
            name='type',
            field=models.CharField(choices=[('LCD', 'LCD'), ('Fan', 'Fan'), ('Sw', 'Switch'), ('Ser', 'Servo')], max_length=10),
        ),
    ]
