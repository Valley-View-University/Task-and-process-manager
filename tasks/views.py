from django.shortcuts import render,HttpResponse
from django.db.models import Model
import json
from accounts.models import CustomUser
from random import choice
from django.shortcuts import get_object_or_404
import json
from django.forms import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models.fields.files import ImageFieldFile
from django.views.decorators.csrf import csrf_exempt
from tasks.models import *




def getRelatedName(model,field):
    return model._meta.get_field(field).model.__name__

# Utitlity classes and functions (For json parsing of objects)
class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, ImageFieldFile):
            try:
                mypath = o.path
            except:
                return ''
            else:
                return mypath
        # this will either recusively return all atrributes of the object or return just the id
        elif isinstance(o, Model):
            return model_to_dict(o)
             # return o.id
        return super().default(o)


# Create your views here.
class Activity:
    # class constructor, initializer
    # TODO: look for a better way to get these models automatically
    def __init__(self,modelName):
        self.modelName = modelName
        self.objects = {'User':CustomUser,
        'Task':Task,
        'SubTask':SubTask,
        'TaskFile':TaskFile
        }

    # class method, creates instances for given models using fields
    # Goes on to add children to the model if specified
    def create(self,models,**kwargs):
        """
        This method creates instances of given modelname(s) 
        using key,val pair from fields keyword arguments. Children
        are added if a list of them are added.
        """
        results = []
        for model in models:
            instance = None
            try:
            # creating instance as django model object based on passed modelName string
                instance = self.objects[model['modelname']]()
            # This error may usually be KeyError
            except Exception as e:
                model_result = {'parent':instance,'children':[],'message':str(e)}
            else:
                for key,val in model['fields'].items():
                    try:
                        if key == "password":
                            password = make_password(val)
                            instance.__setattr__(key,password)
                        else:
                            instance.__setattr__(key,val)
                    except:
                        pass
                try:
                    instance.save()
                except Exception as e:
                    model_result = {'parent':None,'children':[],'message':str(e)}
                else:
                    children = []
                    child_instance = None
                    # Does the model have any children?
                    try:
                        model['children']
                    except Exception as e:
                        model_result = {'parent':instance,'children':[],'message':str(e)}
                    else:
                        for child in model['children']:
                            if isinstance(child['fields'], Model):
                                child_instance = child['fields']
                                try:
                                    if child['child_type'] == "many_to_many":
                                        instance.__setattr__(child['child_name'],[child_instance,])
                                    else:
                                        instance.__setattr__(child['child_name'],child_instance)
                                except:
                                    pass
                                else:
                                    instance.save()
                            # were ids given for child instances?
                            elif 'ids' in child['fields'].keys():
                                print(child['fields']['ids'])
                                # child_instance = self.objects[child['modelname']].__getattr__.get('id',child['fields']['ids'])
                                # if child['child_type'] == "many_to_many":
                                #     instance.__setattr__(child['child_name'],[child_instance,])
                                # else:
                                #     instance.__setattr__(child['child_name'],child_instance)
                                # instance.save()
                            else:
                                try:
                                    child_instance = self.objects[child['modelname']]()
                                except Exception as e:
                                    children.append(child_instance)  
                                else:
                                    for key,val in child['fields'].items():
                                        try:
                                            child_instance.__setattr__(key,val)
                                        except:
                                            pass
                                    # try saving child instance
                                    try:
                                        child_instance.save()
                                    except:
                                        pass
                                    else:
                                        try:
                                            if child['child_type'] == "many_to_many":
                                                instance.__setattr__(child['child_name'],[child_instance,])
                                            else:
                                                instance.__setattr__(child['child_name'],child_instance)
                                        except:
                                            pass
                                        else:
                                            instance.save()
                            children.append(child_instance)     
                        model_result = {'parent':instance,'children':children}
            results.append(model_result)
        return {'success':True,'message':'successful','objects':results}
        


    # reads from database the particular model instance given
    # DONE: add specific field to be returned as **fields
    def read(self,key_id,primary_key,*fields):
        """
        This method will return an object containing all
        the fields and values of the instance requested. 
        key id tell the field that represents the primary key
        and primary key is the given value for the particular instance
        we want.
        If fields are given, then only those fields with their values
        will be returned. Fields that exist on the instance model 
        but do not contain or have values will not be returned
        """
        # setting the model based on passed model string
        # and getting all fields of the model
        allfields = self.objects[self.modelName]._meta.get_fields()
        # setting instance as passed instance
        instance = self.objects[self.modelName].__getattr__.get(key_id,primary_key)
        names = []
        vals = []
        # here we get all the available fields on a particular instance
        # this means if the field is not yet created for the instance
        #  but exists on the model, 
        # it will not be taken
        objects = {}
        # This will use user defined field when returning the object requested
        if fields:
            for field in fields:
                try:
                    val = (getattr(instance, field))
                except:
                    pass
                else:
                    names.append(field)
                    try:
                        obj = list(val.values())
                    except:
                        vals.append(val)
                    else:
                        vals.append(obj)
            for i,e in enumerate(names):
                objects[e]=vals[i]

        else:
            # this will return all available fields on the instance
            for field in allfields:
                try:
                    val = (getattr(instance, field.name))
                except:
                    pass
                else:
                    names.append(field.name)
                    try:
                        obj = list(val.values())
                    except:
                        vals.append(val)
                    else:
                        vals.append(obj)
            for i,e in enumerate(names):
                objects[e]=vals[i]
            # our return dictionary contains fields with 
            # their values even ManyToMany or related field
            # Already serialized
        dump = json.dumps(objects,cls=ExtendedEncoder)
        return {'success':True,'data':dump}

    # class method to update object
    def update(self,key_id,primary_key,**kwargs):
        """
        This method will update a given model instance
        using the given key id and its value:primary key 
        """
        try:
            # instance = self.objects[self.modelName].__getattr__.get(key_id,primary_key)
            instance = self.objects[self.modelName].objects.get(id=primary_key)
        except Exception as e:
            return {'success':False,'message':str(e)}
        else:
            for key,val in kwargs.items():
                if key != key_id:
                    # normal field and foreignkey will work fine here
                    try:
                        instance.__setattr__(key,val)
                    except:
                        # let's check if it is a many to many field
                        # if isinstance(key, ManyToManyField):
                        if key.__class__.__name__ == 'ManyRelatedManager':
                            # Let's loop though the items in the array
                            # and get the objects of the items (which are ids)
                            # let's check if we are creating objects or using ids
                            items = [getRelatedName(self.objects[self.modelName],key).get("id",i) for i in val]
                            instance.__setattr__(key,items)
                            instance.save()
                    else:
                        instance.save()
                    instance.save()
        return {'success':True,'message':'successfully updated'}


    # class method to delete instance of the model
    def delete(self,key_id,primary_key):
        """
        This method simply deletes the given instance primary id
        """
        try:
            instance = self.objects[self.modelName].__getattr__.get(key_id,primary_key)
        except Exception as e:
            return {'success':False,'message':str(e)}
        else:
            instance.delete()
            return {'success':True,'message':'successfully deleted'}


# @csrf_exempt
# def updateTask(request):
#     json_data = json.loads(str(request.body, encoding='utf-8'))
#     objects = {}
#     # This for loop contructs key,val pairs
#     # from incoming request body of api call
#     for key,val in json_data.items():
#         objects[key] = val
#     activity = Activity('Task')
#     execution = activity.update('id',objects['id'],**objects)
#     print(execution)
#     response = {}
#     dump = json.dumps(response,cls=ExtendedEncoder)
#     return HttpResponse(dump, content_type='application/json')
    




@csrf_exempt
def createUser(request):
    """
    Example of how the structure of models to be created should look
    like after receiving all the information from the api call
    trying to create the user object.

    Below makes an example of creating 2 users with GPS child for each
    example = [
            {"modelname":"Buyer",
            "fields":{
                "username":"TheoElia",
                "password":"hellothere22",
                "momo_number":"+233203592400"
            },
            "children":[
                {
                    "modelname":"Specialty",
                    "child_name":"specialties",
                    "child_type":"many_to_many",
                    "fields":{
                        "name":"Capentry"
                    }
                }
            ]
            },
            {
                "modelname":"Seller",
                "fields":{
                    "username":"Fred",
                    "password":"Freddy234",
                    "momo_number":"+233558544343"
                },
            "children":[
                {
                    "modelname":"Specialty",
                    "child_name":"specialties",
                    "child_type":"many_to_many",
                    "fields":{
                        "name":"Painting"
                    }
                }
            ]   
            }
        ]

    """   
    json_data = json.loads(str(request.body, encoding='utf-8'))
    objects = {}
    # This for loop contructs key,val pairs
    # from incoming request body of api call
    for key,val in json_data.items():
        objects[key] = val
    activity = Activity('User')
    models=objects['models']
    # Any validation should have already been done
    execution = activity.create(models)
    # if everything went as expected
    response = {}
    if execution['success']:
        data = execution['objects']
        response = {}
        response['data']=data
        response['success']=True
        # error = ""
        # DONE: create sos account for the user(s) as well.
        # credits = []
        # compounding all user objects created
        # for each in data:  
        #     if each['parent']:   
        #         user = each['parent']
        #         credits.append(user)
        #     else:
        #         error = each['message']
        # Did we create at least one user object? 
        # Then let's generate Sos Account for them
        # if len(credits) > 0:
        #     bundle = createSos(credits)
        #     if bundle['success']: 
        #         credit = {'sos_accounts':bundle['objects']}
        #         data.append(credit)
        #         response['message']= "Created user account(s)"
        #         response['success'] = True
        #         # response['data']=data 
        #     else:
        #         response['message'] = "Could not create Sos accounts"
        #         response['success'] = True
        #         # response['data']=data
        # else:
        #     response['success'] = False
        #     response['message'] = error
        
    else:
        response = {'success':False,'message':'User was not created'}
    dump = json.dumps(response,cls=ExtendedEncoder)
    return HttpResponse(dump, content_type='application/json')

@csrf_exempt
def createTask(request):
    # this gives data being received from api call (payload)
    json_data = json.loads(str(request.body, encoding='utf-8'))
    print(json_data)
    response = {"success":True}
    dump = json.dumps(response,cls=ExtendedEncoder)
    return HttpResponse(dump, content_type='application/json')



@csrf_exempt
def updateTask(request):
    # this gives data being received from api call (payload)
    json_data = json.loads(str(request.body, encoding='utf-8'))
    print(json_data)
    # create an object of CRUD handler
    activity = Activity("Task")
    id = json_data['id']
    del json_data['id']
    execution = activity.update("id",id,**json_data)
    print("execution:",execution)
    response = {"success":True}
    dump = json.dumps(response,cls=ExtendedEncoder)
    return HttpResponse(dump, content_type='application/json')


@csrf_exempt
def updateSubTask(request):
    # this gives data being received from api call (payload)
    json_data = json.loads(str(request.body, encoding='utf-8'))
    print(json_data)
    # create an object of CRUD handler
    activity = Activity("SubTask")
    id = json_data['id']
    del json_data['id']
    execution = activity.update("id",id,**json_data)
    print("execution:",execution)
    subtask = SubTask.objects.get(id=id)
    mytask = subtask.task
    # for task in mytask.tasks.all():
    #     n = 0
    for i in mytask.tasks.all():
        if i.status == "completed":
            n += 1
    perc = round(n/len(task.tasks.all())*100,0)
    percs.append(perc)
    response = {"success":True,'perc':perc}
    dump = json.dumps(response,cls=ExtendedEncoder)
    return HttpResponse(dump, content_type='application/json')