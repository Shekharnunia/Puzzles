from django import forms
from django.contrib import admin
from .models import Article, ArticleComment

from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'user', 'status')
	list_filter = ('user', 'status', 'timestamp')

admin.site.register(ArticleComment)
