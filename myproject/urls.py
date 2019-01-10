from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

from main import views as main_view
from ckeditor_uploader import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('contact-us/', main_view.ContactUs.as_view(), name='contact_us'),
    path('assignments/', include('assignment.urls')),
    path('polls/', include('polls.urls')),
    path('articles/', include('blog.urls')),
    path('main/', include('main.urls')),
    url(r'^account/', include('account.urls')),
    path('control/', include('control_panel.urls')),
    path('newsletter/', include('Newsletter.urls')),
    url(r'^qa/', include('qa.urls')),
    
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^upload/', (views.upload), name='ckeditor_upload'),
    url(r'^browse/', never_cache(views.browse), name='ckeditor_browse'),


    url(r'^admin/', admin.site.urls),  

]

urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_URL)
urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns