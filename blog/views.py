from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.urls import reverse


from .helpers import AuthorRequiredMixin
from .models import Article
from .forms import ArticleForm


class ArticlesListView(LoginRequiredMixin, ListView):
    """Basic ListView implementation to call the published articles list."""
    model = Article
    paginate_by = 5
    context_object_name = "articles"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self, **kwargs):
        return Article.objects.get_published()


class DraftsListView(ArticlesListView):
    """Overriding the original implementation to call the drafts articles
    list."""
    def get_queryset(self, **kwargs):
        return Article.objects.get_drafts()


class CreateArticleView(LoginRequiredMixin, CreateView):
    """Basic CreateView implementation to create new articles."""
    model = Article
    message = ("Your article has been created.")
    form_class = ArticleForm
    template_name = 'blog/article_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse('blog:list')


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
        messages.success(self.request, self.message)
        return reverse('blog:list')


class DetailArticleView(LoginRequiredMixin, DetailView):
    """Basic DetailView implementation to call an individual article."""
    model = Article

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.object.pk) 
        if not self.request.session.get(session_key, False):
            self.object.views += 1
            self.object.save()
            self.request.session[session_key] = True   
        return super().get_context_data(**kwargs)



class TagArticlesListView(ArticlesListView):
    """Overriding the original implementation to call the drafts articles
    list."""
    def get_queryset(self, **kwargs):
        return Article.objects.filter(tags__name=self.kwargs['tag_name']).filter(status='P')

