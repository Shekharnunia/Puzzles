import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify
from taggit.managers import TaggableManager


class Post(models.Model):
    DRAFT = "D"
    PUBLISHED = "P"
    STATUS = (
        (DRAFT, _("Draft")),
        (PUBLISHED, _("Published")),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name="author",
        on_delete=models.SET_NULL)
    image = models.ImageField(
        _('Featured image'), upload_to='articles_pictures/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, null=False, unique=True)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    content = MarkdownxField()
    edited = models.BooleanField(default=False)
    tags = TaggableManager()
    objects = ArticleQuerySet.as_manager()



    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=140, unique = True)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    published_date = models.DateTimeField(blank=True, null=True)
    views = models.IntegerField(default = 0)
    slug = models.SlugField(max_length=100, unique=True)
    draft = models.BooleanField(default=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ("-timestamp",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user.username}-{self.title}",
                                to_lower=True, max_length=80)

        super().save(*args, **kwargs)

    def get_markdown(self):
        return markdownify(self.content)




#class Comment(models.Model):
#    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
#    author = models.CharField(max_length=200)
#    text = models.TextField()
#    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)
#    approved_comment = models.BooleanField(default=False)
#
#    def approve(self):
#        self.approved_comment = True
#        self.save()
#
#    def __str__(self):
#        return self.text
