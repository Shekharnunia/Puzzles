from django import forms

from qa.models import Answer, Question

from pagedown.widgets import PagedownWidget


class QuestionForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    content = forms.CharField(widget=PagedownWidget())

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "status"]


class AnswerForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget())

    class Meta:
        model = Answer
        fields = ["content", ]
