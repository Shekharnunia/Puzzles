from django.contrib import admin

from .models import Article, ArticleComment, Category


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status')
    list_filter = ('user', 'status', 'timestamp')

    class Meta:
        model = Article


admin.site.register(Article, ArticleAdmin)

admin.site.register(ArticleComment)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Category, CategoryAdmin)
