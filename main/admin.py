# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from main.models import Question, Answer, ContactUs, NewsLetter


class QuestionAdmin(admin.ModelAdmin):
	list_display = ['topic', 'question', 'created_by']

	class Meta:
	    model = Question


class ContactUsAdmin(admin.ModelAdmin):
	list_display = ['name', 'email', 'message']

	class Meta:
	    model = ContactUs


class AnswerAdmin(admin.ModelAdmin):
	list_display = ['question_a', 'answer', 'answer_by']

	class Meta:
	    model = Answer

admin.site.register(Question, QuestionAdmin)

admin.site.register(Answer, AnswerAdmin)

admin.site.register(ContactUs, ContactUsAdmin)

admin.site.register(NewsLetter)
