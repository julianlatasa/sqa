# Generated by Django 4.0.2 on 2022-02-27 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_rename_garminactivity_garminactivities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='garminactivities',
            name='date',
        ),
        migrations.AddField(
            model_name='garminactivities',
            name='datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
