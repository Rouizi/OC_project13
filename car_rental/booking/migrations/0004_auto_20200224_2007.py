# Generated by Django 3.0.3 on 2020-02-24 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_reservationdeal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='createdeal',
            old_name='created_at',
            new_name='created_on',
        ),
        migrations.AddField(
            model_name='reservationdeal',
            name='reserved_on',
            field=models.DateTimeField(auto_now_add=True, default='2020-02-01'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='createdeal',
            name='available',
            field=models.BooleanField(default=True),
        ),
    ]
