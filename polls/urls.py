from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='poll'),
    path('create', views.create, name='create'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:question_id>/results/', views.results, name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]


#app_name = 'polls'
#urlpatterns = [
#    path('', views.IndexView.as_view(), name='poll'),
#    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
#    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    path('<int:question_id>/vote/', views.vote, name='vote'),
#]
