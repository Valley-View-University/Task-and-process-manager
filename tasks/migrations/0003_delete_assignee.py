# Generated by Django 2.2.3 on 2020-04-14 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_assignee_assignee'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Assignee',
        ),
    ]
