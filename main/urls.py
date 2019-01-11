from django.conf.urls import url
from main import views

from .models import Question


app_name = 'main'
urlpatterns = [	   
    url(r'^$', views.questionlistview, name='home'),
    url(r'^ask-question/$', views.CreateQuestionView.as_view(), name='ask_question'),
        
    url(r'^question/(?P<pk>\d+)/$', views.question, name='question'),

#    url(r'^question/(?P<pk>\d+)/delete$', views.delete_question, name= 'delete_question'),
    url(r'^question/(?P<pk>\d+)/delete$', views.DeleteQuestionView.as_view(), name='delete_question'),

#    url(r'^answer/(?P<pk_a>\d+)/delete$', views.delete_answer, name= 'delete_answer'),
    url(r'^answer/(?P<pk>\d+)/delete$', views.DeleteAnswerView.as_view(), name='delete_answer'),
    
    url(r'^question/(?P<pk>\d+)/edit/$', views.QuestionEditView.as_view(), name='edit_question'),
    url(r'^answer/(?P<pk>\d+)/edit/$', views.AnswerEditView.as_view(), name='edit_answer'),

]
