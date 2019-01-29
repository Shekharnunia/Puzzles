from django import forms


class CommentForm(forms.Form):
    content_type = forms.CharField(label='',widget=forms.HiddenInput)
    object_id = forms.IntegerField(label='',widget=forms.HiddenInput)
    #parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='')
