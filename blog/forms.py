from django import forms
from pagedown.widgets import PagedownWidget

from .models import Article, ArticleComment


class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    content = forms.CharField(widget=PagedownWidget())
    edited = forms.BooleanField(
        widget=forms.HiddenInput(), required=False, initial=False)

    class Meta:
        model = Article
        fields = ["title", 
        "categories", 
        "thumbnail", 
        "content", 
        "allow_comments",
        "show_comments_publically",
        "tags", 
        "status", 
        "edited", ]


class ArticleCommentForm(forms.ModelForm):

    class Meta:
        model = ArticleComment
        fields = ["comment", ]
