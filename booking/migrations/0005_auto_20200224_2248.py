# Generated by Django 3.0.3 on 2020-02-24 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_auto_20200224_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservationdeal',
            name='reserved_on',
            field=models.DateField(auto_now_add=True),
        ),
    ]