from django.shortcuts import render,redirect
from .models import *
from tasks.models import Task



links = [
{'link':'navbar-dashboards','icon':'shop','color':'red', 'name':'Quick Links','active':False,'dropdown':True,
'dropdowns':
[
    {'link':'/','icon':'collection', 'name':'My dashboard','active':True},
    {'link':'/admin','icon':'world-2', 'name':'Admin','active':False}
]
},


# {'link':'navbar-examples','icon':'palette','color':'green','name':'Utils','active':False,'dropdown':True,
# 'dropdowns':
# [{'link':"https://www.onlinegdb.com",'icon':'html5', 'name':'Code Online','active':False},
# {'link':'/accounts/utils/prepare_roaster/','icon':'calendar-grid-58', 'name':'Prepare Rooster','active':False},
# {'link':"/accounts/utils/grouping/",'icon':'istanbul', 'name':'Prepare Grouping','active':False},
# {'link':"/accounts/utils/add_todo/",'icon':'active-40', 'name':'Add Todo Item','active':False},
# {'link':"/value_mysite/",'icon':'active-40', 'name':'Value Site','active':False}
# ]
# },
{'link':'navbar-pages','icon':'circle-08','color':'pink','name':'Account','active':False,'dropdown':True,
'dropdowns':
[{'link':'/accounts/logout/','icon':'user-run', 'name':'Logout','active':False}]
}
# {'link':'navbar-components','icon':'app','color':'blue','name':'ChatBot','active':False,'dropdown':True,
# 'dropdowns':
# [{'link':'/api/v1/robot/admin/','icon':'bullet-list-67', 'name':'Bot Admin','active':False},
# {'link':'/api/v1/robot/train_view/','icon':'controller', 'name':'Train bot','active':False},]
# }
]

# Create your views here.
def index(request):
    if request.user.is_authenticated:
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
            args['links']=links
        return render(request,template_name,args)
    return redirect("/admin/login/?next=/")
