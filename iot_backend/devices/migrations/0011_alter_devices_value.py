# Generated by Django 4.1.3 on 2023-05-05 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0010_alter_devicehst_time_stamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devices',
            name='value',
            field=models.DecimalField(decimal_places=3, max_digits=10, null=True),
        ),
    ]