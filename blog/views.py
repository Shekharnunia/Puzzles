from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  RedirectView, UpdateView)
from django.http import JsonResponse

from taggit.models import Tag

from decorators import ajax_required
from helpers import AuthorRequiredMixin, TeacherRequiredMixin

from .forms import ArticleCommentForm, ArticleForm
from .models import Article, ArticleComment, Category


class CategoryListView(LoginRequiredMixin, ListView):
    """Basic ListView implementation to call the published articles list."""
    model = Category
    context_object_name = "categorys"


class CategoryDetailView(LoginRequiredMixin, DetailView):
    """Basic DetailView implementation to call an individual article."""
    model = Category
    context_object_name = "category"


class ArticlesListView(LoginRequiredMixin, ListView):
    """Basic ListView implementation to call the published articles list."""
    model = Article
    paginate_by = 5
    context_object_name = "articles"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['popular_tags'] = Article.objects.get_counted_tags()
        context['categories'] = Category.objects.all()
        context['popular'] = Article.objects.get_5_popular_post()
        context['search_url'] = reverse('blog:results')
        return context

    def get_queryset(self, **kwargs):
        return Article.objects.select_related("user", "categories").prefetch_related("articlecomment_set", "tagged_items__tag").get_published()


class DraftsListView(ArticlesListView):
    """Overriding the original implementation to call the drafts articles
    list."""

    def get_queryset(self, **kwargs):
        return Article.objects.get_drafts()


class PopularListView(ArticlesListView):
    """Overriding the original implementation to call the popular articles
    list."""

    def get_queryset(self, **kwargs):
        return Article.objects.get_popular_post()


class SearchListView(LoginRequiredMixin, ListView):
    """CBV to contain all the search results"""
    model = Article
    paginate_by = 10
    context_object_name = "articles"

    def get_queryset(self, *args, **kwargs):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            return Article.objects.filter(Q(
                title__icontains=query) | Q(content__icontains=query) | Q(
                tags__name__icontains=query) | Q(
                user__username__icontains=query) | Q(
                categories__title__icontains=query), status="P").distinct()
        else:
            return Article.objects.get_published()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search'] = True
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            context["extra"] = '&query={}'.format(query)
            article = self.object_list
            context['article_count'] = article.count()
            return context
        return context


class CreateArticleView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """Basic CreateView implementation to create new articles."""
    model = Article
    message = ("Your article has been created.")
    form_class = ArticleForm
    template_name = 'blog/article_create.html'

    def form_valid(self, form):
        blog = form.save(commit=False)
        blog.user = self.request.user
        blog.save()
        form.save_m2m()
        messages.success(self.request, self.message)
        return redirect(blog.get_absolute_url())


class EditArticleView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    """Basic EditView implementation to edit existing articles."""
    model = Article
    message = ("Your article has been updated.")
    form_class = ArticleForm
    template_name = 'blog/article_update.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        blog = self.get_object()
        messages.success(self.request, self.message)
        return blog.get_absolute_url()


class DeleteArticleView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    """Basic EditView implementation to edit existing articles."""
    model = Article
    message = ("Your article has been deleted.")
    template_name = 'blog/article_delete_confirm.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse('blog:list')


class DetailArticleView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Basic DetailView implementation to call an individual article."""
    model = Article

    def get_context_data(self, *args, **kwargs):
        session_key = 'viewed_article_{}'.format(self.object.pk)
        if not self.request.session.get(session_key, False):
            self.object.views += 1
            self.object.save()
            self.request.session[session_key] = True
        context = super().get_context_data(*args, **kwargs)
        context['categories'] = Category.objects.all()
        context['is_liked'] = self.object.likes.filter(id=self.request.user.id).exists()
        context['popular'] = Article.objects.get_5_popular_post()
        if self.object.allow_comments == True or self.object.user == self.request.user:
            context['comment_show'] = True
            if self.object.show_comments_publically == True or self.object.user == self.request.user:
                context['user_comments'] = self.object.get_comments()
            else:
                context['user_comments'] = self.object.get_comments().filter(
                    Q(user=self.request.user) |
                    Q(user=self.object.user)
                )
        else:
            context['comment_show'] = False
        return context

    def test_func(self):
        blog = self.get_object()
        if self.request.user == blog.user or blog.status == 'P':
            return True
        return False


class TagArticlesListView(ArticlesListView):
    """Overriding the original implementation to call the tag articles
    list."""

    def get_queryset(self, **kwargs):
        return Article.objects.filter(tags__name=self.kwargs['tag_name']).filter(status='P')


@login_required
@ajax_required
def comment(request):
    try:
        if request.method == 'POST':
            article_id = request.POST.get('article')
            article = Article.objects.get(pk=article_id)
            comment = request.POST.get('comment')
            comment = comment.strip()
            if len(comment) > 0:
                article_comment = ArticleComment(user=request.user,
                                                 article=article,
                                                 comment=comment)
                article_comment.save()
            html = ''

            if article.show_comments_publically == True or article.user == request.user:
                user_comments = article.get_comments()
            else:
                user_comments = article.get_comments().filter(
                    Q(user=request.user) |
                    Q(user=article.user)
                )
            for comment in user_comments:
                html = '{0}{1}'.format(html, render_to_string(
                    'blog/partial_article_comment.html',
                    {'comment': comment}))

            return HttpResponse(html)

        else:   # pragma: no cover
            return HttpResponseBadRequest()

    except Exception:   # pragma: no cover
        return HttpResponseBadRequest()


@login_required
def like_post(request):
    article = get_object_or_404(Article, id=request.POST.get('id'))
    is_liked = False
    if article.likes.filter(id=request.user.id).exists():
        article.likes.remove(request.user)
        is_liked = False
    else:
        article.likes.add(request.user)
        is_liked = True
    context = {
        'article': article,
        'is_liked': is_liked,
        'total_likes': article.likes.count(),
    }
    if request.is_ajax():
        html = render_to_string('blog/like_section.html', context, request=request)
        return JsonResponse({'form': html})
