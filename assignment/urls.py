from django.urls import path

from . import views

app_name='assignment'
urlpatterns = [
	path('', views.AssignmentListView.as_view(), name='list'),
	path('create/', views.AssignmentCreateView.as_view(), name='create'),
	path('<slug:slug>/<int:int>/', views.AssignmentDetailView.as_view(), name='detail'),
	path('<slug:slug>/<int:int>/edit/', views.AssignmentEditView.as_view(), name='edit'),
	path('<slug:slug>/<int:int>/delete/', views.AssignmentDeleteView.as_view(), name='delete'),
]