# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tests.testapp.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('related_field', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent_field', models.IntegerField()),
                ('datetime_field', models.DateTimeField(help_text=b'Date time field')),
                ('date_field', models.DateField(help_text=b'Date field')),
                ('time_field', models.TimeField(help_text=b'Date field')),
                ('char_field', models.CharField(help_text=b'Char field', max_length=50)),
                ('choices_field', models.CharField(default=b'a', max_length=1, choices=[(b'a', b'Choice 1'), (b'b', b'Choice 2')])),
                ('text_field', models.TextField(help_text=b'Text field')),
                ('float_field', models.FloatField(help_text=b'Float field')),
                ('decimal_field', models.DecimalField(default=100.0, null=True, max_digits=10, decimal_places=5, blank=True)),
                ('integer_field', models.IntegerField(default=tests.testapp.models.get_default, help_text=b'Integer field', null=True)),
                ('boolean_field', models.BooleanField(default=False)),
                ('file_field', models.FileField(help_text=b'File field', upload_to=b'media', verbose_name=b'File')),
                ('related_field', models.ForeignKey(to='testapp.RelatedModel')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
