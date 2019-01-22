from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'assignment'
urlpatterns = [
    path('', views.AssignmentListView.as_view(), name='list'),
    path('all/', views.AllAssignmentListView.as_view(), name='all_list'),
    path('new/', views.AssignmentNewestListView.as_view(), name='new_list'),
    path('old/', views.AssignmentOldestListView.as_view(), name='old_list'),
    path('draft/', views.AssignmentDraftListView.as_view(), name='draft_list'),
    path('create/', views.AssignmentCreateView.as_view(), name='create'),

    url(r'^assignment/(?P<pk>\d+)/delete$',
        views.StudentAssignmentDeleteView.as_view(),
        name='delete_assignment'),

    url(r'^assignment/(?P<pk>\d+)/edit/$',
        views.StudentAssignmentEditView.as_view(),
        name='edit_assignment'),

    path('<slug:slug>/<int:pk>/',
         views.assignment_detail_view,
         name='detail'
         ),

    path('<slug:slug>/<int:int>/edit/',
         views.AssignmentEditView.as_view(),
         name='edit'
         ),

    path('<slug:slug>/<int:int>/delete/',
         views.AssignmentDeleteView.as_view(),
         name='delete'
         ),

    url(r'^tag/(?P<tag_name>.+)/$',
        views.TagAssignmentListView.as_view(),
        name='tag'
        ),
]
