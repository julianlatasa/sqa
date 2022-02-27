# Generated by Django 4.0.2 on 2022-02-27 02:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0018_alter_cachedata_cache_alter_cachedata_garmincookies'),
    ]

    operations = [
        migrations.AddField(
            model_name='athletecoach',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.plan'),
        ),
        migrations.AddField(
            model_name='garminactivity',
            name='garmin_file',
            field=models.BinaryField(blank=True),
        ),
        migrations.AddField(
            model_name='garminactivity',
            name='garmin_object',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='garminactivity',
            name='garmin_sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.garminsport'),
        ),
        migrations.AlterField(
            model_name='garminactivity',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='PlanActivities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(blank=True, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('activity', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.activity')),
                ('plan', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.plan')),
            ],
        ),
    ]
