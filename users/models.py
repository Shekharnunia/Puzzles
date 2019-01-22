from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from blog.models import Article, ArticleComment
from qa.models import Question, Answer
from assignment.models import Assignment


class User(AbstractUser):
    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField(_("User's name"), blank=True, max_length=255)
    picture = models.ImageField(
        _('Profile picture'), upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(
        _('Location'), max_length=50, null=True, blank=True)
    job_title = models.CharField(
        _('Job title'), max_length=50, null=True, blank=True)
    personal_url = models.URLField(
        _('Personal URL'), max_length=555, blank=True, null=True)
    facebook_account = models.URLField(
        _('Facebook profile'), max_length=255, blank=True, null=True)
    twitter_account = models.URLField(
        _('Twitter account'), max_length=255, blank=True, null=True)
    github_account = models.URLField(
        _('GitHub profile'), max_length=255, blank=True, null=True)
    linkedin_account = models.URLField(
        _('LinkedIn profile'), max_length=255, blank=True, null=True)
    short_bio = models.CharField(
        _('Describe yourself'), max_length=60, blank=True, null=True)
    bio = models.CharField(
        _('Short bio'), max_length=280, blank=True, null=True)
    is_student = models.BooleanField('student status', default=False)
    is_teacher = models.BooleanField('teacher status', default=False)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def get_profile_name(self):
        if self.name:
            return self.name

        return self.username

    def get_article_count(self):
        return Article.objects.filter(user=self).count()

    def get_question_count(self):
        return Question.objects.filter(user=self).count()

    def get_answer_count(self):
        return Answer.objects.filter(user=self).count()

    def get_assignment_count(self):
        if self.is_teacher == True:
            return Assignment.objects.filter(uploader=self).count()
        elif self.is_student == True:
            return 0

    def get_comments_count(self):
        return ArticleComment.objects.filter(user=self).count()
