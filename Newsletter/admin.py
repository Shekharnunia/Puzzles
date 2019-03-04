from django.contrib import admin

from .models import NewsLetter, NewsLetterUser


class NewsLetterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_added',)


admin.site.register(NewsLetterUser, NewsLetterUserAdmin)

admin.site.register(NewsLetter)
