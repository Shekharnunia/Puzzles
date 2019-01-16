from django import forms

from .models import Assignment

class AssignmentForm(forms.ModelForm):
    topic = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 1, 'placeholder': 'keep it short and to the point...'}
        ),
        # max_length=1500,
        # help_text='The max length of the text is 4000.'
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 10,
                'placeholder': 'What is in your mind?',
            }
        ),
    )
    class Meta:
        model = Assignment
        fields = [
            'topic',
            'description',
            'assignment_file',
            'tags', 
            'draft'
        ]
