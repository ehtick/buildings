# Generated by Django 3.1.2 on 2021-11-10 16:47

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0027_dxfimport_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dxfimport',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', max_length=18),
        ),
    ]
