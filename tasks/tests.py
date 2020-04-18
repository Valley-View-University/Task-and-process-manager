from django.test import TestCase
from .models import Task,SubTask,TaskFile

# Create your tests here.
res = Task._meta.get_field('assignees').model.__name__
print(res)
# print(help(res))
