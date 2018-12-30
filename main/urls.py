from django.conf.urls import url
from django.contrib import admin
from main import views

app_name = 'main'
urlpatterns = [	   
    url(r'^$', views.QuestionListView.as_view(),name='home'),
    url(r'^ask-question/$', views.CreateQuestionView.as_view(), name='ask_question'),
    url(r'^privacy-policy/$', views.privacy_policy, name='privacy_policy'),
    url(r'^term-and-conditions/$', views.term_and_conditions, name='term_and_conditions'),
    url(r'^contact-us/$', views.ContactUs.as_view(), name='contact_us'),    
    url(r'^question/(?P<pk>\d+)/$', views.question, name='question'),

#    url(r'^question/(?P<pk>\d+)/delete$', views.delete_question, name= 'delete_question'),
    url(r'^question/(?P<pk>\d+)/delete$', views.DeleteQuestionView.as_view(), name='delete_question'),

#    url(r'^answer/(?P<pk_a>\d+)/delete$', views.delete_answer, name= 'delete_answer'),
    url(r'^answer/(?P<pk>\d+)/delete$', views.DeleteAnswerView.as_view(), name='delete_answer'),
    
    url(r'^question/(?P<pk>\d+)/edit/$', views.QuestionEditView.as_view(), name='edit_question'),
    url(r'^answer/(?P<pk>\d+)/edit/$', views.AnswerEditView.as_view(), name='edit_answer'),

]
