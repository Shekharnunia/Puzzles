from django import forms
from django.contrib import admin
from .models import Article, ArticleComment

from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class ArticleAdmin(admin.ModelAdmin):
	content_image = forms.CharField(widget=CKEditorUploadingWidget())
	list_display = ('title', 'user', 'status')
	list_filter = ('user', 'status', 'timestamp')
	class Meta:
		model = Article


admin.site.register(Article, ArticleAdmin)

admin.site.register(ArticleComment)
