import uuid
from collections import Counter

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.db.models import Count

from django.urls import reverse

from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe

from markdown import markdown
from taggit.managers import TaggableManager



class Vote(models.Model):
    """Model class to host every vote, made with ContentType framework to
    allow a single model connected to Questions and Answers."""
    uuid_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType,
        blank=True, null=True, related_name="votes_on", on_delete=models.CASCADE)
    object_id = models.CharField(
        max_length=50, blank=True, null=True)
    vote = GenericForeignKey(
        "content_type", "object_id")

    class Meta:
        verbose_name = _("Vote")
        verbose_name_plural = _("Votes")
        index_together = ("content_type", "object_id")
        unique_together = ("user", "content_type", "object_id")




class QuestionQuerySet(models.query.QuerySet):
    """Personalized queryset created to improve model usability"""

    def get_answered(self):
        """Returns only items which has been marked as answered in the current
        queryset"""
        return self.filter(has_answer=True)

    def get_unanswered(self):
        """Returns only items which has not been marked as answered in the
        current queryset"""
        return self.filter(has_answer=False)

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





class Question(models.Model):
    """Model class to contain every question in the forum."""
    OPEN = "O"
    CLOSED = "C"
    DRAFT = "D"
    STATUS = (
        (OPEN, _("Open")),
        (CLOSED, _("Closed")),
        (DRAFT, _("Draft")),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300, unique=True, blank=False)
    content = models.TextField(blank=False)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    question_views = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    total_votes = models.IntegerField(default=0)
    votes = GenericRelation(Vote)
    favorites = models.IntegerField(default=0)
    has_answer = models.BooleanField(default=False)
    tags = TaggableManager()
    objects = QuestionQuerySet.as_manager()

    class Meta:
        ordering = ["total_votes", "-timestamp"]
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.id}")
                                

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def count_answers(self):
        return Answer.objects.filter(question=self).count()

    def count_votes(self):
        """Method to update the sum of the total votes. Uses this complex query
        to avoid race conditions at database level."""
        dic = Counter(self.votes.values_list("value", flat=True))
        Question.objects.filter(id=self.id).update(total_votes=dic[True] - dic[False])
        self.refresh_from_db()

    def get_upvoters(self):
        """Returns a list containing the users who upvoted the instance."""
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        """Returns a list containing the users who downvoted the instance."""
        return [vote.user for vote in self.votes.filter(value=False)]

    def get_answers(self):
        return Answer.objects.filter(question=self)

    def get_accepted_answer(self):
        return Answer.objects.get(question=self, is_answer=True)

    def get_markdown(self):
        return markdownify(self.content)

    def get_absolute_url(self):
        return reverse("main:question", kwargs={"pk": self.pk, "slug":self.slug})

    def get_markdown(self):
        return mark_safe(markdown(self.content, safe_mode='escape'))








class Answer(models.Model):
    """Model class to contain every answer in the forum and to link it
    to its respective question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    uuid_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    total_votes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_answer = models.BooleanField(default=False)
    votes = GenericRelation(Vote)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_answer", "-timestamp"]
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")

    def __str__(self):  # pragma: no cover
        return self.content

    def get_absolute_url(self):
        return reverse("main:question", kwargs={"pk": self.question_a.pk})

    def get_markdown(self):
        return mark_safe(markdown(self.content, safe_mode='escape'))

    def count_votes(self):
        """Method to update the sum of the total votes. Uses this complex query
        to avoid race conditions at database level."""
        dic = Counter(self.votes.values_list("value", flat=True))
        Answer.objects.filter(uuid_id=self.uuid_id).update(total_votes=dic[True] - dic[False])
        self.refresh_from_db()

    def get_upvoters(self):
        """Returns a list containing the users who upvoted the instance."""
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        """Returns a list containing the users who downvoted the instance."""
        return [vote.user for vote in self.votes.filter(value=False)]

    def accept_answer(self):
        answer_set = Answer.objects.filter(question=self.question)
        answer_set.update(is_answer=False)
        self.is_answer = True
        self.save()
        self.question.has_answer = True
        self.question.save()


