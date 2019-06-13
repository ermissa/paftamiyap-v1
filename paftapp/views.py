import os.path
import json
from django.shortcuts import render
from django.db import DatabaseError, transaction
from django.db.models import Q
from .models import *
from django.contrib.auth import authenticate,login , logout as django_logout
from django.http import HttpResponseRedirect , HttpResponse , JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.shortcuts import redirect,get_object_or_404
from django.conf import settings
from .forms import *
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


def home(request):
    try:
        form_context = {}
        form_context['project_form'] = ProjectForm()
        form_context['customer_form'] = CustomerForm()
        
        if request.method == "GET":
            return render(request,'home.html',form_context)
        
        elif request.method == "POST":
            project_form = ProjectForm(request.POST,request.FILES)
            customer_form = CustomerForm(request.POST)
            if project_form.is_valid() and customer_form.is_valid():
                project = project_form.save(commit=False)
                customer = customer_form.save()
                project.customer = customer
                # for i in range(40): # Used to create test data
                #     project.pk = None
                project.save()

                project_form.save_m2m()
                messages.success(request,'Proje kaydınız başarıyla oluşturuldu. Sizinle en kısa zamanda irtibata geçeceğiz. Esen kalın.')
            else:
                print("---> NonValid Form")
                messages.error(request,"Proje kaydınız yapılırken bir hata meydana geldi. Gerekli alanları doldurduğunuzdan emin olup tekrar deneyin.")
            return redirect('home')
    except Exception as e:
        print("---> Exception: ",str(e))
        messages.error(request,"Proje kaydınız yapılırken bir hata meydana geldi. Lütfen Tekrar deneyiniz.")
        return redirect('home')



def project_detail(request,id):
    print("---> views.project_detail")
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_id = request.user.id
            project = Project.objects.get(pk = id)
            #ClickedUsers.objects.filter(user = request.user , project = project).update(status = 1)
            ClickedUsers.objects.update_or_create(user = request.user , project = project,defaults={'status' : 1})
            print("---> Path : ",project.documentation_path)
            if not os.path.exists(str(project.documentation_path)):
                print("----> Dosya Yok")
                project.documentation_path = None

            context = { 'project' : project}
            return render(request, 'dashboard_project_detail.html',context)
        else:
            return redirect('login')


def dashboard(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            #projects_list = Project.objects.prefetch_related('clicked_users').filter(clicked_users = request.user)
            #projects_list = Project.objects.filter(clicked_users__id = request.user.id).prefetch_related('clicked_users')
            #projects_list = ClickedUsers.objects.filter(user_id = request.user.id).select_related('project')
            projects_list = Project.objects.filter(Q(project_status = 0)).order_by('-id')
            print("---> PROJEC LISTESI : ", projects_list.values() ,"\n", projects_list.query)
            paginator = Paginator(projects_list,8)
            
            page = request.GET.get('page',1)
            projects = paginator.get_page(page)
            clicked_projects = ClickedUsers.objects.filter(user = request.user,status=1).values('project')
            #print("------>CLİCKED PROJECT" , clicked_projects , [i['project'] for i in clicked_projects])
            
            context = {'projects' : projects , 'clicked_projects' : [i['project'] for i in clicked_projects]}
            return render(request, 'dashboard_main.html',context)
        else:
            return redirect('login')
    
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username , password = password)
        if user is not None:
            login(request,user)
            projects_list = Project.objects.all()
            paginator = Paginator(projects_list,8)
            
            page = request.GET.get('page',1)
            projects = paginator.get_page(page)
            context = {'projects' : projects}
            return redirect('dashboard')
        else:
            return redirect('home')

def login_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:    
            return redirect('dashboard')
        else:
            return render(request, 'login.html')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username , password = password)
        if user is not None:
            login(request,user)
            projects_list = Project.objects.all()
            paginator = Paginator(projects_list,8)
            
            page = request.GET.get('page',1)
            projects = paginator.get_page(page)
            context = {'projects' : projects}
            return redirect('dashboard')
        else:
            return redirect('login')
    

def logout_view(request):
    django_logout(request)
    return redirect('login')


def download_file(request,id):
    if request.method == 'GET':
        if request.user.is_authenticated:    
            obj = get_object_or_404(Project, pk=id)
            ext = str(obj.documentation_path).split('.')[-1]
            content_type = "application/" + ext
            response = HttpResponse(
                obj.documentation_path,
                content_type=content_type)

            response['Content-Disposition'] = 'attachment;filename=' + str(obj.documentation_path)
            return response



@csrf_exempt
def update_is_called(request):
    if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                id = body['id']
                Project.objects.filter(id=id).update(is_called=(Q(is_called=False) | Q(is_called=None)))
                return JsonResponse({'value' : 'success'},status=200)
            else:
                print("----> LOGIN REDIRECT")
                return JsonResponse({'error': 'unauthorized'}, status=401)
        except Exception as e:
            print("---> Exception: ",str(e))
            return JsonResponse({'error': str(e)}, status=401)