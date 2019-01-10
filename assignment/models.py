from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect

from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


def assignment_upload_path(instance, filename):
	return 'assignment/user_{0}/{1}'.format(instance.uploader.username, filename)



class AssignmentQuerySet(models.query.QuerySet):
    """Personalized queryset created to improve model usability"""

    def get_assignment(self):
        """Returns only items which has not been marked as draft in the current
        queryset"""
        return self.filter(draft=False)

    def get_draft_assignment(self):
        """Returns only items which has not been marked as draft in the
        current queryset"""
        return self.filter(draft=True)

    def get_counted_tags(self):
        """Returns a dict element with tags and its count to show on the UI."""
        tag_dict = {}
        query = self.all().annotate(tagged=Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1

                else:  # pragma: no cover
                    tag_dict[tag] += 1

        return tag_dict.items()


class Assignment(models.Model):
	uploader = models.ForeignKey(User, on_delete = models.CASCADE)
	slug = models.SlugField(max_length=50, blank=False)
	topic = models.CharField(max_length=240, blank=False)
	description = RichTextUploadingField()
	assignment_file = models.FileField(upload_to=assignment_upload_path, blank=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	assignment_views = models.PositiveIntegerField(default=0)
	draft = models.BooleanField(default=False, null=True, blank=True)
	tags = TaggableManager()
	objects = AssignmentQuerySet.as_manager()

	class Meta:
		ordering = ['-timestamp',]

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

	def get_summary(self):
		if len(self.description) > 255:
			return '{0}...'.format(self.description[:255])

		else:
			return self.description
