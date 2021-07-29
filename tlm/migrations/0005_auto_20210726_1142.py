# Generated by Django 3.2.4 on 2021-07-26 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlm', '0004_auto_20210724_1758'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', models.BigIntegerField()),
                ('chat_id', models.BigIntegerField()),
            ],
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('cid',), name='unique_cid'),
        ),
    ]