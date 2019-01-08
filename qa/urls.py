from django.conf.urls import url
from django.urls import path

from qa import views

app_name = 'qa'
urlpatterns = [
    url(r'^$', views.QuestionListView.as_view(), name='index_noans'),
    url(r'^answered/$', views.QuestionAnsListView.as_view(), name='index_ans'),
    path('indexed/', views.QuestionsIndexListView.as_view(), name='index_all'),
    url(r'^ask-question/$', views.CreateQuestionView.as_view(), name='ask_question'),
    url(r'^question-detail/(?P<pk>\d+)/$', views.QuestionDetailView.as_view(), name='question_detail'),
    url(r'^question-detail/(?P<pk>\d+)/close/$', views.QuestionDetaiCloseView.as_view(), name='question_close'),
    url(r'^question-detail/(?P<pk>\d+)/edit/$', views.EditQuestionView.as_view(), name='edit_question'),
    url(r'^question-detail/(?P<pk>\d+)/delete/$', views.DeleteQuestionView.as_view(), name='delete_question'),
    url(r'^propose-answer/(?P<question_id>\d+)/$', views.CreateAnswerView.as_view(), name='propose_answer'),
    path('question-detail/<int:pk>/detele-answer/<uuid:answer_id>/', views.DeleteAnswerView.as_view(), name='delete_answer'),
    path('question-detail/<int:pk>/edit-answer/<uuid:answer_id>/', views.EditAnswerView.as_view(), name='edit_answer'),
    url(r'^question/vote/$', views.question_vote, name='question_vote'),
    url(r'^answer/vote/$', views.answer_vote, name='answer_vote'),
    url(r'^accept-answer/$', views.accept_answer, name='accept_answer'),
    url(r'^tag/(?P<tag_name>.+)/$', views.TagQuestionListView.as_view(), name='tag'),
]
