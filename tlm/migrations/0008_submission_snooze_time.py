# Generated by Django 3.2.5 on 2021-07-27 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlm', '0007_rename_assignee_submission_target_chat_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='snooze_time',
            field=models.DateTimeField(null=True),
        ),
    ]
