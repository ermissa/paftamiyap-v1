from django.conf.urls import url
from django.contrib import admin
from django.urls import path, re_path,include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    path('' , views.home,name = "home"),
    path('projects/<int:id>/', views.project_detail),
    path('update_is_called', views.update_is_called),
    path('login', views.login_view , name="login"),
    path('logout', views.logout_view , name="logout"),
    path('dashboard', views.dashboard , name="dashboard"),
    path('download/<int:id>/', views.download_file , name="download"),
]
