from django.conf import settings
from django.conf.urls import url,include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

#from account import views as core_views

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('blog/', include('blog.urls')),
    url(r'',include('main.urls',namespace='main')),
    url(r'account/',include('account.urls',namespace='account')),


    url(r'^admin/', admin.site.urls),  

]

urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_URL)
urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
