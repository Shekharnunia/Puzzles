from django.conf.urls import url
from django.urls import path
from Newsletter import views

app_name = 'control_panel'

urlpatterns = [	   
    path('newsletter/', views.control_newsletter, name='control_newsletter'),
]
