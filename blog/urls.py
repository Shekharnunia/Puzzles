from django.conf.urls import url

from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^categories/(?P<slug>[-\w]+)/$',
        views.CategoryDetailView.as_view(),
        name='category_detail'
        ),

    url(r'^search/$', views.SearchListView.as_view(), name='results'),


    url(r'^categories/$',
        views.CategoryListView.as_view(),
        name='category_list'
        ),

    url(r'^$',
        views.ArticlesListView.as_view(),
        name='list'),

    url(r'^write-new-article/$',
        views.CreateArticleView.as_view(),
        name='write_new'),

    url(r'^drafts/$',
        views.DraftsListView.as_view(),
        name='drafts'),

    url(r'^popular/$',
        views.PopularListView.as_view(),
        name='popular'),

    url(r'^comment/$',
        views.comment,
        name='comment'),

    url(r'^edit/(?P<pk>\d+)/$',
        views.EditArticleView.as_view(),
        name='edit_article'),

    url(r'^delete/(?P<pk>\d+)/$',
        views.DeleteArticleView.as_view(),
        name='delete_article'),

    url(r'^(?P<pk>\d+)/like/$',
        views.PostLikeToggle.as_view(),
        name='like-toggle'),

    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[-\w]+)/$',
        views.DetailArticleView.as_view(),
        name='article'),

    url(r'^tag/(?P<tag_name>.+)/$',
        views.TagArticlesListView.as_view(),
        name='tag'),
]
