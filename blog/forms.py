from django import forms

from .models import Article, ArticleComment


class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    edited = forms.BooleanField(
        widget=forms.HiddenInput(), required=False, initial=False)

    class Meta:
        model = Article
        fields = ["title", "content", "image", "tags", "status", "edited"]
        

class ArticleCommentForm(forms.ModelForm):

    class Meta:
        model = ArticleComment
        fields = ["comment",]        
