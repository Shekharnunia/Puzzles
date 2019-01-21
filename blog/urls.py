from django.conf.urls import url
from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$',
        views.ArticlesListView.as_view(),
        name='list'),

    url(r'^write-new-article/$',
        views.CreateArticleView.as_view(),
        name='write_new'),

    url(r'^drafts/$',
        views.DraftsListView.as_view(),
        name='drafts'),

    url(r'^comment/$',
        views.comment,
        name='comment'),

    url(r'^edit/(?P<pk>\d+)/$',
        views.EditArticleView.as_view(),
        name='edit_article'),

    url(r'^delete/(?P<pk>\d+)/$',
        views.DeleteArticleView.as_view(),
        name='delete_article'),

    url(r'^(?P<slug>[-\w]+)/$',
        views.DetailArticleView.as_view(),
        name='article'),

    url(r'^tag/(?P<tag_name>.+)/$',
        views.TagArticlesListView.as_view(),
        name='tag'),
]
