from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.text import slugify
from markdown import markdown
from taggit.managers import TaggableManager

from comments.models import Comment


def assignment_upload_path(instance, filename):
    return 'assignment/teacher/user_{0}/{1}'.format(
        instance.uploader.username,
        filename
    )


class AssignmentQuerySet(models.query.QuerySet):
    """Personalized queryset created to improve model usability"""

    def get_assignment(self):
        """Returns only items which has not been marked as draft in the current
        queryset"""
        return self.filter(draft=False).order_by('-timestamp')

    def get_draft_assignment(self, request):
        """Returns only items which has not been marked as draft in the
        current queryset"""
        return self.filter(draft=True).filter(uploader=request.user).order_by('-timestamp')

    def get_assignment_of_a_teacher(self):
        """Returns only items which has not been marked as draft in the current
        queryset"""
        return self.filter(draft=False).filter(uploader=self.uploader).order_by('-timestamp')

    def get_oldest_student(self):
        """Returns only items which has been posted oldest and are not draft
                for students queryset"""
        return self.filter(draft=False).order_by('timestamp')

    def get_newest_student(self):
        """Returns only items which has been posted newest and are not draft
        for students queryset"""
        return self.filter(draft=False).order_by('-timestamp')

    def get_counted_tags(self):
        """Returns a dict element with tags and its count to show on the UI."""
        tag_dict = {}
        query = self.filter(draft=False).annotate(
            tagged=Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1

                else:  # pragma: no cover
                    tag_dict[tag] += 1

        return tag_dict.items()

    def search(self, query):
        return self.filter(Q(
            topic__icontains=query) | Q(description__icontains=query) | Q(
            tags__name__iexact=query) | Q(
            uploader__username__iexact=query), draft=False).distinct()

    def draft_search(self, query, request):
        return self.filter(Q(
            topic__icontains=query) | Q(description__icontains=query) | Q(
            tags__name__iexact=query) | Q(
            uploader__username__iexact=query), draft=True, uploader=request.user).distinct()


def student_assignment_upload_path(instance, filename):
    return 'assignment/student/user_{0}/{1}'.format(
        instance.user.username,
        filename
    )


class Assignment(models.Model):
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    slug = models.SlugField(max_length=50, blank=False)
    topic = models.CharField(max_length=240, blank=False)
    description = models.TextField()
    assignment_file = models.FileField(
        upload_to=assignment_upload_path,
        blank=False
    )
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    assignment_views = models.PositiveIntegerField(default=0)
    draft = models.BooleanField(default=False, null=True)
    tags = TaggableManager()
    objects = AssignmentQuerySet.as_manager()

    # class Meta:
    #     ordering = ['-timestamp', ]

    def __str__(self):
        return self.topic

    # class Meta:
        # ordering = ('-timestamp', '-pk')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.topic[:50])

        super(Assignment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.assignment_file.delete()
        super().delete(*args, **kwargs)

    def get_absolute_url(self, *args, **kwargs):
        return reverse("assignment:detail",
                       kwargs={"pk": self.pk, "slug": self.slug})

    def get_description_as_markdown(self):
        return mark_safe(markdown(self.description, safe_mode='escape'))

    def get_summary(self):
        if len(self.get_description_as_markdown()) > 255:
            return '{0}...'.format(self.get_description_as_markdown()[:255])

        else:
            return self.get_description_as_markdown()

    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return content_type


class StudentAssignment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    feedback = models.TextField(null=True, blank=True)
    assignment_file = models.FileField(
        upload_to=student_assignment_upload_path,
        blank=False
    )
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        ordering = ['-timestamp', ]

    def __str__(self):
        return '{0}{1}...'.format(self.user, self.feedback[:25])
        return self.user

    def delete(self, *args, **kwargs):
        self.assignment_file.delete()
        super().delete(*args, **kwargs)

    def get_feedback_as_markdown(self):
        return mark_safe(markdown(self.feedback, safe_mode='escape'))

    def get_summary(self):
        if len(self.get_feedback_as_markdown()) > 255:
            return '{0}...'.format(self.get_feeback_as_markdown()[:255])

        else:
            return self.get_feedback_as_markdown()

    def get_absolute_url(self):
        return reverse("assignment:detail",
                       kwargs={"pk": self.assignment.pk, "slug": self.assignment.slug})
