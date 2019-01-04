from django.conf import settings
from django.conf.urls import url,include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from blog import views

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('articles/', include('blog.urls')),
    path('', include('main.urls')),
    url(r'^account/', include('account.urls')),
    path('control/', include('control_panel.urls')),
    path('newsletter/', include('Newsletter.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^qa/', include('qa.urls')),

    url(r'^admin/', admin.site.urls),  

]

urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_URL)
urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
