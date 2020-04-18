from django.shortcuts import render
from .models import *
from tasks.models import Task

# Create your views here.
def index(request):
    template_name = "accounts/employee.html"
    args = {}
    #tasks = Task.objects.filter(assignees__id=request.user.id)#.order_by("-start_date")
    tasks = Task.objects.filter(assigned_by=request.user)
    if tasks:
        percs = []
        for task in tasks:
            n = 0
            for i in task.tasks.all():
                if i.status == "completed":
                    n += 1
            perc = round(n/len(task.tasks.all())*100,0)
            percs.append(perc)
        mytasks = zip(tasks,percs)
        args['ergents']=mytasks
    return render(request,template_name,args)
