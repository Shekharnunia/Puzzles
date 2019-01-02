from django import forms

from .models import NewsLetterUser, NewsLetter
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class NewsLetterUserSignupForm(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email@example.com'}),label='')
    class Meta:
        model = NewsLetterUser
        fields = ['email']

        def clean_email(self):
            email = self.cleaned_data.get('email')
            return email




class NewsLetterCreationForm(forms.ModelForm):

    class Meta:
        model = NewsLetter
        fields = ['subject', 'body', 'email', 'status']

        def clean_email(self):
            email = self.cleaned_data.get('email')

            return email
