from django.conf.urls import url
from django.urls import path

from Newsletter import views

app_name = 'control_panel'

urlpatterns = [
    path('newsletter/',
         views.control_newsletter,
         name='control_newsletter'),

    path('newsletter/<int:pk>/',
         views.newsletter_detail,
         name='control_newsletter_detail'),

    path('newsletter/<int:pk>/edit/',
         views.control_newsletter_edit,
         name='control_newsletter_edit'),

    path('newsletter/<int:pk>/delete/',
         views.NewsletterDeleteView.as_view(),

         name='control_newsletter_delete'),

    path('newsletter-list/',
         views.NewsletterListView.as_view(),

         name='control_newsletter_list'),
]
