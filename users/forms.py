from django import forms


STATUS= [
    ('is_teacher', 'teacher'),
    ('is_student', 'student'),
    ]

class SignupForm(forms.Form):
	status = forms.CharField(label='What is your status?', widget=forms.Select(choices=STATUS))

	def signup(self, request, user):
		if self.cleaned_data['status'] == 'is_teacher':
			user.is_teacher = True
		if self.cleaned_data['status'] == 'is_student':
			user.is_student = True
		user.save()