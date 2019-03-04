import datetime

import readtime
from django.conf import settings
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from markdown import markdown
from taggit.managers import TaggableManager


class ArticleQuerySet(models.query.QuerySet):
    """Personalized queryset created to improve model usability"""

    def get_published(self):
        """Returns only the published items in the current queryset."""
        return self.filter(status="P")

    def get_drafts(self):
        """Returns only the items marked as DRAFT in the current queryset."""
        return self.filter(status="D")

    def get_5_popular_post(self):
        """Returns only the popular items as in the current queryset."""
        return self.order_by('-views')[:5]

    def get_popular_post(self):
        """Returns only the popular items as in the current queryset."""
        return self.order_by('-views')

    def get_counted_tags(self):
        tag_dict = {}
        query = self.filter(status='P').annotate(
            tagged=Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1

                else:  # pragma: no cover
                    tag_dict[tag] += 1

        return tag_dict.items()


class Category(models.Model):
    """Category model."""
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    summary = models.TextField(max_length=600)
    thumbnail = models.ImageField(
        ('Category image'), upload_to='category/')

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    def get_articles(self):
        return Article.objects.filter(categories=self)


class Article(models.Model):
    DRAFT = "D"
    PUBLISHED = "P"
    STATUS = (
        (DRAFT, ("Draft")),
        (PUBLISHED, ("Published")),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name="author",
        on_delete=models.SET_NULL)
    thumbnail = models.ImageField(
        ('thumbnail image'), upload_to='articles_pictures/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    title = models.CharField(max_length=255, null=False, unique=True)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    content = models.TextField()
    edited = models.BooleanField(default=False)
    tags = TaggableManager()
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='likes')

    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = ("Article")
        verbose_name_plural = ("Articles")
        ordering = ("-timestamp",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:article', kwargs={
            'year': self.timestamp.year,
            'month': self.timestamp.strftime("%m"),
            'day': self.timestamp.strftime("%d"),
            'slug': self.slug
        })

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.thumbnail.delete()
        super().delete(*args, **kwargs)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.content, safe_mode='escape'))

    def get_summary(self):
        if len(self.get_message_as_markdown()) > 255:
            return '{0}...'.format(self.get_message_as_markdown()[:255])

        else:
            return self.get_message_as_markdown()

    def get_comments(self):
        return ArticleComment.objects.filter(article=self)

    def get_readtime(self):
        return readtime.of_html(self.content)

    def get_like_url(self):
        return reverse("blog:like-toggle", kwargs={"pk": self.pk})


class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = ("Article Comment")
        verbose_name_plural = ("Article Comments")
        ordering = ("date",)

    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.article.title)
