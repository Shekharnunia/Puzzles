from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'Newsletter'

urlpatterns = [	   
    path('subscribe/', views.newsletter_signup, name='newsletter_signup'),
    path('unsubscribe/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
]
