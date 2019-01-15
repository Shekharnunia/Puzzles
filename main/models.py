from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe



class Question(models.Model):
    topic = models.CharField(max_length=300,unique=True)
    question = models.TextField(max_length=4000, blank=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    question_views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-pk",)

    def __str__(self):
        return self.topic

    def get_absolute_url(self):
        return reverse("main:question", kwargs={"pk": self.pk})

    def get_topic_as_markdown(self):
        return mark_safe(markdown(self.topic, safe_mode='escape'))

    def get_question_as_markdown(self):
        return mark_safe(markdown(self.question, safe_mode='escape'))



class Answer(models.Model):
    question_a = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer = models.TextField(max_length=1500,blank=False)
    answer_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answer_by')
    answers_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    answer_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.answer

    def get_absolute_url(self):
        return reverse("main:question", kwargs={"pk": self.question_a.pk})

    def get_answer_as_markdown(self):
        return mark_safe(markdown(self.answer, safe_mode='escape'))


class ContactUs(models.Model):
    name = models.CharField(max_length=50, blank=False,)
    email = models.EmailField()
    subject = models.CharField(max_length = 256)
    message = models.TextField(max_length=2000, blank=False)

    def __str__(self):
        return self.email
