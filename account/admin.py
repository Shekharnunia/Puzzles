from __future__ import unicode_literals

from django.contrib import admin

from .models import UserProfile



class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','phone','city','country')


    def get_queryset(self, request):
        queryset = super(UserProfileAdmin, self).get_queryset(request)
        queryset = queryset.order_by('-phone', 'user')
        return queryset

admin.site.register(UserProfile, UserProfileAdmin)
