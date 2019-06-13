import uuid
import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .validators import *

def content_file_name(instance, filename):
    _datetime = datetime.datetime.now()
    datetime_str = _datetime.strftime("%Y-%m-%d_%H-%M-%S")
    ext = filename.split('.')[-1]
    filename = "%s_%s.%s" % (datetime_str,uuid.uuid4(), ext)
    return os.path.join('uploads/', filename)


class Software(models.Model):
    #fields
    name = models.CharField(max_length = 200)
    image_path = models.FileField(upload_to='uploads/%Y/%m/%d/',validators=[file_size,FileExtensionValidator(allowed_extensions=['pdf'])],blank=True, null=True)


class MapSheet(models.Model):
    #fields
    size = models.CharField(max_length = 200)
    
    def __str__(self):
        return '%s' % self.size

class Customer(models.Model):
    name = models.CharField(max_length = 60)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(max_length=200)


class Project(models.Model):
    #fields
    deadline = models.DateField(null=False)
    has_model = models.BooleanField()
    has_render = models.BooleanField()
    description = models.CharField(max_length = 1000)
    # documentation_path = models.FileField(upload_to='uploads/%Y/%m/%d/',blank=True, null=True,validators=[file_size,FileExtensionValidator(allowed_extensions=['pdf','png','jpeg','jpg'])])
    documentation_path = models.FileField(upload_to=content_file_name,blank=True, null=True,validators=[file_size,FileExtensionValidator(allowed_extensions=['pdf','png','jpeg','jpg'])])
    is_called = models.BooleanField(blank=True,null=True,default=False)
    
    # Active 0 , Passive (Closed,Done etc.) 1
    project_status = models.IntegerField(default=0)

    #foreign keys
    map_sheet = models.ForeignKey(
        MapSheet,
        on_delete = models.CASCADE,
        null = False
    )
    customer = models.ForeignKey(
        Customer,
        on_delete = models.CASCADE,
        null=False
    )

    softwares = models.ManyToManyField(Software,blank=True)
    clicked_users = models.ManyToManyField(User,through='ClickedUsers',blank=True,related_name="clickedusers")

    def save(self,*args, **kwargs):
        super(Project,self).save(*args, **kwargs)        
        ClickedUsers.objects.bulk_create([ClickedUsers(user = i , project = self) for i in list(User.objects.all())])

    def clean(self, *args, **kwargs):
        # run the base validation
        super(Project, self).clean(*args, **kwargs)

        # Don't allow deadline dates older than now.
        if self.deadline < datetime.date.today():
            raise ValidationError('Deadline must be later than now.')


class ClickedUsers(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user")
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    
    # 0 for nonclicked , 1 for clicked. Maybe 2 for another status in future.
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
