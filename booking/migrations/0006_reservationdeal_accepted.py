# Generated by Django 3.0.3 on 2020-02-24 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_auto_20200224_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationdeal',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]