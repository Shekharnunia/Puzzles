import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.models import User
from django.utils.text import slugify
import markdown
from taggit.managers import TaggableManager


class ArticleQuerySet(models.query.QuerySet):
    """Personalized queryset created to improve model usability"""

    def get_published(self):
        """Returns only the published items in the current queryset."""
        return self.filter(status="P")

    def get_drafts(self):
        """Returns only the items marked as DRAFT in the current queryset."""
        return self.filter(status="D")

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
    image = models.ImageField(
        ('Featured image'), upload_to='articles_pictures/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    title = models.CharField(max_length=255, null=False, unique=True)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    content = models.TextField()
    edited = models.BooleanField(default=False)
    tags = TaggableManager()
    objects = ArticleQuerySet.as_manager()
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    views = models.PositiveIntegerField(default = 0)



    class Meta:
        verbose_name = ("Article")
        verbose_name_plural = ("Articles")
        ordering = ("-timestamp",)

    def __str__(self):
        return self.title

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    def get_summary(self):
        if len(self.content) > 255:
            return '{0}...'.format(self.content[:255])

        else:
            return self.content

    def get_comments(self):
        return ArticleComment.objects.filter(article=self)



class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = ("Article Comment")
        verbose_name_plural = ("Article Comments")
        ordering = ("date",)

    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.article.title)


    def get_comment_as_markdown(self):
        return markdown.markdown(self.comment, safe_mode='escape')
