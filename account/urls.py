from django.conf.urls import url
from account import views as account_views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.urls import path

app_name = 'account'
urlpatterns = [	   
    url(r'^login/$', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    # url(r'^login/$', account_views.login_view, name='login'),
    
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    
    url(r'^register/$', account_views.register, name='register'),

    url(r'^profile/(?P<username>[a-zA-Z0-9]+)$', account_views.profile, name='profile'),
    # url(r'^profile/(?P<username>[a-zA-Z0-9]+)/edit/$', account_views.UserUpdateView.as_view(), name='edit_profile'),
    
    
    url(r'^change-password/$', auth_views.PasswordChangeView.as_view(template_name='account/change_password.html', success_url = reverse_lazy('account:password_change_done')),
        name='change_password'),
    url(r'^password-change_done/$', auth_views.PasswordChangeDoneView.as_view(template_name='account/change_password_done.html'),
        name='password_change_done'),

    # url(r'^reset-password/$', auth_views.password_reset, {'template_name': 'account/reset_password.html', 'post_reset_redirect': 'account:password_reset_done', 'email_template_name': 'account/reset_password_email.html'}, name='reset_password'),
    # url(r'^reset-password/done/$', auth_views.password_reset_done, {'template_name': 'account/reset_password_done.html'}, name='password_reset_done'),
    # url(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'template_name': 'account/reset_password_confirm.html', 'post_reset_redirect': 'account:password_reset_complete'}, name='password_reset_confirm'),
    # url(r'^reset-password/complete/$', auth_views.password_reset_complete,{'template_name': 'account/reset_password_complete.html'}, name='password_reset_complete'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name= 'account/reset_password.html', email_template_name = 'account/reset_password_email.html', success_url = reverse_lazy('account:password_reset_done')), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name= 'account/reset_password_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = 'account/reset_password_confirm.html', success_url = reverse_lazy('account:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name= 'account/reset_password_complete.html'), name='password_reset_complete'),



    url(r'^accounts/update/(?P<pk>[\-\w]+)/$', account_views.edit_user, name='account_update'),
]
