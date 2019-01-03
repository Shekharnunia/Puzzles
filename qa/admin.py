from django.contrib import admin

from qa.models import Question, Answer


class QuestionAdmin(admin.ModelAdmin):
	list_display = ['topic', 'question', 'created_by']

	class Meta:
	    model = Question


class AnswerAdmin(admin.ModelAdmin):
	list_display = ['question_a', 'answer', 'answer_by']

	class Meta:
	    model = Answer

admin.site.register(Question)

admin.site.register(Answer)

