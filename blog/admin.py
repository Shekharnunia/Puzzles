from django.contrib import admin

from .models import Comment, Post



class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1


class PostAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['title', 'description', 'draft']}),
        ('Date information', {'fields': ['published_date'], 'classes': ['collapse']}),
    ]
    inlines = [CommentInline]

    list_display = ('title','description', 'author', 'published_date', 'draft', 'was_published_recently')

admin.site.register(Post, PostAdmin)

