from django.conf import settings
from django.conf.urls import url,include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

#from account import views as core_views

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('blog/', include('blog.urls')),
    url(r'',include('main.urls',namespace='main')),
#    url(r'account/',include('account.urls',namespace='account')),

    url(r'^accounts/profile/$', TemplateView.as_view(template_name='account/profile.html')),

    url(r'^admin/', admin.site.urls),  

    url(r'^accounts/', include('allauth.urls')),

]

urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_URL)
urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
