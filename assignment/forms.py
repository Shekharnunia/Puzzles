from django import forms
from pagedown.widgets import PagedownWidget

from .models import Assignment, StudentAssignment


class AssignmentForm(forms.ModelForm):
    topic = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 1, 'placeholder': 'keep it short and to the point...'}
        ),
        # max_length=1500,
        # help_text='The max length of the text is 4000.'
    )
    description = forms.CharField(
        widget=PagedownWidget(
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


class StudentAssignmentForm(forms.ModelForm):
    class Meta:
        model = StudentAssignment
        fields = [
            'assignment_file',
            'feedback',
        ]
