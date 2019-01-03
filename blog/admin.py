from django.contrib import admin
from .models import Article, ArticleComment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status')
    list_filter = ('user', 'status', 'timestamp')

admin.site.register(ArticleComment)
