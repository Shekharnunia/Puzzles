from django.db import models
from django.conf import settings
# Create your models here.

class NewsLetterUser(models.Model):
    email = models.EmailField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class NewsLetter(models.Model):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    EMAIL_STATUS_CHOICES = (
        (DRAFT, ("Draft")),
        (PUBLISHED, ("Published")),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, default='1')
    subject = models.CharField(max_length=250)
    body = models.TextField(max_length=5000)
    email = models.ManyToManyField(NewsLetterUser)
    status = models.CharField(max_length=10, choices=EMAIL_STATUS_CHOICES, default='Draft')
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)


    class Meta:
        ordering = ("-pk",)

    def __str__(self):
        return self.subject


