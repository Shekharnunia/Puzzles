from django.conf.urls import url
from django.urls import path
from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('posts/<slug:slug>/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/new', views.post_new, name='post_new'),
    path('posts/<slug:slug>/<int:pk>/edit', views.post_edit, name='post_edit'),
    path('drafts/', views.post_draft_list, name='post_draft_list'),
    path('post/<pk>/publish/', views.post_publish, name='post_publish'),
    path('post/<pk>/remove/', views.post_remove, name='post_remove'),
#    url(r'^post/(?P<slug>[-\w]+)/(?P<pk>\d+)/comment/$', views.add_comment_to_post, name='add_comment_to_post'),
#    url(r'^comment/(?P<pk>\d+)/approve/$', views.comment_approve, name='comment_approve'),
#    url(r'^comment/(?P<pk>\d+)/remove/$', views.comment_remove, name='comment_remove'),
]
