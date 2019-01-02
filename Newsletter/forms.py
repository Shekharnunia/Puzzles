from django import forms

from .models import NewsLetterUser, NewsLetter
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class NewsLetterUserSignupForm(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}),label='')
    class Meta:
        model = NewsLetterUser
        fields = ['email']

        def clean_email(self):
            email = self.cleaned_data.get('email')
            return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='form-group offset-3'),
                Submit('submit', 'Subscribe', css_class='btn input-group-append', id="button-addon2"),
                css_class='input-group mb-3 form-row'
            ),

        )




class NewsLetterCreationForm(forms.ModelForm):

    class Meta:
        model = NewsLetter
        fields = ['subject', 'body', 'email', 'status']

        def clean_email(self):
            email = self.cleaned_data.get('email')

            return email
