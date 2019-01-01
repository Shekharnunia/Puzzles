from django.contrib import admin

from .models import NewsLetterUser, NewsLetter

class NewsLetterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_added',)


admin.site.register(NewsLetterUser, NewsLetterUserAdmin)

admin.site.register(NewsLetter)

