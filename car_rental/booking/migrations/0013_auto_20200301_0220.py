# Generated by Django 3.0.3 on 2020-03-01 01:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_auto_20200229_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservationdeal',
            name='deal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.CreateDeal'),
        ),
    ]
