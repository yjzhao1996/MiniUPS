from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('', home_view, name='home_view'),
    path('<int:id>', package_view, name='package_view'),
    path('login/', login_view, name='login_view'),
    path('regist/',regist_view,name='regist_view'),
    path('signout/', sign_out_view, name='sign_out_view'),       
    path('user/<int:pk>/package/waiting/',waiting_packages_view,name='waiting_packages_view'),
    path('user/<int:pk>/package/loading/',loading_packages_view,name='loading_packages_view'),
    path('user/<int:pk>/package/delivering/',delivering_packages_view,name='delivering_packages_view'),
    path('user/<int:pk>/package/delivered/',delivered_packages_view,name='delivered_packages_view'),
    path('user/package_info/<int:pk>/<int:id>/',packages_info_view,name='packages_info_view')
    
]

