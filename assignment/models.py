from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect

from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


def assignment_upload_path(instance, filename):
	return 'assignment/user_{0}/{1}'.format(instance.uploader.username, filename)


class Assignment(models.Model):
	uploader = models.ForeignKey(User, on_delete = models.CASCADE)
	slug = models.SlugField(max_length=50, blank=False)
	topic = models.CharField(max_length=240, blank=False)
	description = RichTextUploadingField()
	assignment_file = models.FileField(upload_to=assignment_upload_path, blank=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	assignment_views = models.PositiveIntegerField(default=0)
	draft = models.BooleanField(default=False)
	tags = TaggableManager()

	def __str__(self):
		return self.topic

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.topic[:50])
		
		super(Assignment, self).save(*args, **kwargs)  # Call the "real" save() method.

	def delete(self, *args, **kwargs):
		assignment_file.delete()
		super().save(*args, **kwargs) 
	    
	def get_absolute_url(self, *args, **kwargs):
		return redirect(reverse('assignment:list', kwargs={self.pk, self.slug}))