from django.contrib import admin
from .models import *


class SubInline(admin.TabularInline):
    model = SubTask
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    model = Task
    inlines = [ SubInline, ]
    list_display = ['id','title']



# Register your models here.
admin.site.register(Task,TaskAdmin)