# Generated by Django 4.0.2 on 2022-02-17 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_remove_profile_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='usertype',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.usertype'),
        ),
    ]
