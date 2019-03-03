from django.conf.urls import url
from django.urls import path

from qa import views

app_name = 'qa'
urlpatterns = [
    url(r'^$', views.QuestionListView.as_view(), name='index_noans'),
    url(r'^answered/$', views.QuestionAnsListView.as_view(), name='index_ans'),
    path('indexed/', views.QuestionsIndexListView.as_view(), name='index_all'),
    url(r'^ask-question/$', views.CreateQuestionView.as_view(), name='ask_question'),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)/$', views.QuestionDetailView.as_view(), name='question_detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)/close/$', views.QuestionDetaiCloseView.as_view(), name='question_close'),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)/edit/$', views.EditQuestionView.as_view(), name='edit_question'),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)/delete/$', views.DeleteQuestionView.as_view(), name='delete_question'),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)/flag/$', views.q_flag, name='flag_question'),
    url(r'^propose-answer/(?P<question_id>\d+)/$', views.CreateAnswerView.as_view(), name='propose_answer'),
    path('<int:pk>/<slug:slug>/detele-answer/<uuid:answer_id>/', views.DeleteAnswerView.as_view(), name='delete_answer'),
    path('<int:pk>/<slug:slug>/edit-answer/<uuid:answer_id>/', views.EditAnswerView.as_view(), name='edit_answer'),
    path('<int:pk>/<slug:slug>/flag/<uuid:answer_id>/', views.a_flag, name='flag_answer'),
    url(r'^question/vote/$', views.question_vote, name='question_vote'),
    url(r'^answer/vote/$', views.answer_vote, name='answer_vote'),
    url(r'^accept-answer/$', views.accept_answer, name='accept_answer'),
    url(r'^tag/(?P<tag_name>.+)/$', views.TagQuestionListView.as_view(), name='tag'),
    url(r'^search/$', views.SearchListView.as_view(), name='results'),
]
