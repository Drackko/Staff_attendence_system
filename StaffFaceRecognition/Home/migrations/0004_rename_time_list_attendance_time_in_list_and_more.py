# Generated by Django 5.1.6 on 2025-02-06 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0003_remove_attendance_time_in_remove_attendance_time_out_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attendance',
            old_name='time_list',
            new_name='time_in_list',
        ),
        migrations.AddField(
            model_name='attendance',
            name='time_out_list',
            field=models.TextField(blank=True, null=True),
        ),
    ]
