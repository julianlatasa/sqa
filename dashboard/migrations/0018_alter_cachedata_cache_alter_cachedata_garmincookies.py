# Generated by Django 4.0.2 on 2022-02-25 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_cachedata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cachedata',
            name='cache',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='cachedata',
            name='garmincookies',
            field=models.TextField(blank=True),
        ),
    ]
