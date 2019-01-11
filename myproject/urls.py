from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from main import views as main_views

from ckeditor_uploader import views
from graphene_django.views import GraphQLView

urlpatterns = [
    path('', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('privacy-policy/', TemplateView.as_view(template_name='main/privacy_policy.html'), name='privacy_policy'),
    path('term-and-conditions/', TemplateView.as_view(template_name='pages/about.html'), name='term_and_conditions'),
    
    path('assignments/', include('assignment.urls')),
    path('polls/', include('polls.urls')),
    path('articles/', include('blog.urls')),
    path('main/', include('main.urls')),
    #url(r'^account/', include('account.urls')),
    url(r'^users/', include('users.urls')),
    path('control/', include('control_panel.urls')),
    path('newsletter/', include('Newsletter.urls')),
    url(r'^qa/', include('qa.urls')),

    path('contact-us/', main_views.ContactUs.as_view(), name='contact_us'),

    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^upload/', (views.upload), name='ckeditor_upload'),
    url(r'^browse/', never_cache(views.browse), name='ckeditor_browse'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^graphql', GraphQLView.as_view(graphiql=True)),

    url(r'^admin/', admin.site.urls),  

]

urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_URL)
urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns