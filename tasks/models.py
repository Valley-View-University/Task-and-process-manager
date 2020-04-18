from django.db import models
from django.conf import settings



stata = (
    ("completed","completed"),
    ("pending","pending"),
    ("cancelled","cancelled"),
    ("in-progress","in-progress")
)

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=50,null=True,help_text="Project name or title")
    description = models.TextField(null=True,help_text="General description of the whole project to be executed")
    assigned_by =  models.ForeignKey(settings.AUTH_USER_MODEL, null=True,on_delete=models.SET_NULL,help_text="This should usually be you")
    created_on = models.DateTimeField(auto_now_add=True)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name="assignees",help_text="All persons on this project")
    status = models.CharField(max_length=20,null=True,choices=stata)

    def __str__(self):
        return self.title


class SubTask(models.Model):
    task = models.ForeignKey(Task, null=True,on_delete=models.SET_NULL,related_name="tasks")
    description = models.TextField(null=True,help_text="What is to be done here")
    start_date = models.DateTimeField(null=True,blank=True)
    end_date = models.DateTimeField(null=True,blank=True)
    status = models.CharField(max_length=20,null=True,choices=stata)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,on_delete=models.SET_NULL,blank=True)   
    agents = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name="agents")


class TaskFile(models.Model):
    task = models.ForeignKey(SubTask, null=True,on_delete=models.SET_NULL,related_name="files")
    name = models.CharField(max_length=50,null=True)
    task_file = models.FileField(upload_to="static/tasks-files")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,on_delete=models.SET_NULL)
    uploaded_on = models.DateTimeField(auto_now_add=True)