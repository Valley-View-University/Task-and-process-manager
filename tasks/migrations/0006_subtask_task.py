# Generated by Django 2.2.3 on 2020-04-14 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_auto_20200414_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtask',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='tasks.Task'),
        ),
    ]
