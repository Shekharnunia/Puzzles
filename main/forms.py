from django import forms
from django.contrib.auth.models import User

from main.models import Question, Answer

class QuestionForm(forms.ModelForm):
    topic = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 1, 'placeholder': 'keep it short and to the point...'}
        ),
        # max_length=1500,
        # help_text='The max length of the text is 4000.'
    )
    question = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 10,
                'placeholder': 'What is in your mind?',
            }
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )
    class Meta:
        model = Question
        fields = [
            'topic',
            'question'
        ]

class AnswerForm(forms.ModelForm):
    answer = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 10, 'placeholder': 'What is in your mind?'}
        ),
        max_length=1500,
        # help_text='The max length of the text is 4000.'
    )
    class Meta:
        model = Answer
        fields = [
            'answer'
        ]

