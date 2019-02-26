from django.contrib import admin

from qa.models import Question, Answer, Vote


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'timestamp']

    class Meta:
        model = Question


class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'user', 'timestamp']

    class Meta:
        model = Answer


admin.site.register(Question, QuestionAdmin)

admin.site.register(Answer, AnswerAdmin)

admin.site.register(Vote)
