from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^tasks/create-task/$', views.createTask,name="create-task"),
    url(r'^tasks/update-task/$', views.updateTask,name="update-task"),
    url(r'^tasks/update-subtask/$', views.updateSubTask,name="update-subtask"),
]