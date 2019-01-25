from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView

from taggit.models import Tag

from blog.models import Article
from assignment.models import Assignment
from helpers import ajax_required
from qa.models import Question


class SearchListView(LoginRequiredMixin, ListView):
    """CBV to contain all the search results"""
    model = Question
    template_name = "search/search_results.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get("query")
        # context["active"] = 'news'
        context["active"] = 'qa'
        context["hide_search"] = True
        context["tags_list"] = Tag.objects.filter(name=query)
        # context["news_list"] = News.objects.filter(
        #     content__icontains=query, reply=False)
        context["articles_list"] = Article.objects.filter(Q(
            title__icontains=query) | Q(content__icontains=query) | Q(
                tags__name__icontains=query), status="P")
        context["assignment_list"] = Assignment.objects.filter(Q(
            topic__icontains=query) | Q(description__icontains=query) | Q(
                tags__name__icontains=query), draft=True)
        context["questions_list"] = Question.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(
                tags__name__icontains=query))
        context["users_list"] = get_user_model().objects.filter(
            Q(username__icontains=query) | Q(
                name__icontains=query))
        # context["news_count"] = context["news_list"].count()
        context["articles_count"] = context["articles_list"].count()
        context["questions_count"] = context["questions_list"].count()
        context["users_count"] = context["users_list"].count()
        context["tags_count"] = context["tags_list"].count()
        context["assignment_count"] = context["assignment_list"].count()
        # context["total_results"] = context["news_count"] + \
        context["articles_count"] + context["questions_count"] + \
            context["users_count"] + context["tags_count"]
        return context


@login_required
def search(request):
    if 'q' in request.GET:
        querystring = request.GET.get('q').strip()
        if len(querystring) == 0:
            return redirect('/search/')

        try:
            search_type = request.GET.get('type')
            if search_type not in ['blog', 'qa', 'users']:
                search_type = 'feed'

        except Exception:
            search_type = 'qa'

        count = {}
        results = {}

        results['articles'] = Article.objects.filter(
            Q(title__icontains=querystring) | Q(
                content__icontains=querystring), status='P')
        results['questions'] = Question.objects.filter(
            Q(title__icontains=querystring) | Q(
                description__icontains=querystring))
        results['users'] = User.objects.filter(
            Q(username__icontains=querystring) | Q(
                first_name__icontains=querystring) | Q(
                    last_name__icontains=querystring))
        # count['feed'] = results['feed'].count()
        count['articles'] = results['articles'].count()
        count['questions'] = results['questions'].count()
        count['users'] = results['users'].count()

        return render(request, 'search/results.html', {
            'hide_search': True,
            'querystring': querystring,
            'active': search_type,
            'count': count,
            'results': results[search_type],
        })

    else:
        return render(request, 'search/search.html', {'hide_search': True})


# For autocomplete suggestions
@login_required
@ajax_required
def get_suggestions(request):
    # Convert users, articles, questions objects into list to be
    # represented as a single list.
    query = request.GET.get('term', '')
    users = list(get_user_model().objects.filter(
        Q(username__icontains=query) | Q(name__icontains=query)))
    articles = list(Article.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query) | Q(
            tags__name__icontains=query), status="P"))
    questions = list(Question.objects.filter(Q(title__icontains=query) | Q(
        content__icontains=query) | Q(tags__name__icontains=query)))
    # Add all the retrieved users, articles, questions to data_retrieved
    # list.
    data_retrieved = users
    data_retrieved.extend(articles)
    data_retrieved.extend(questions)
    results = []
    for data in data_retrieved:
        data_json = {}
        if isinstance(data, get_user_model()):
            data_json['id'] = data.id
            data_json['label'] = data.username
            data_json['value'] = data.username

        if isinstance(data, Article):
            data_json['id'] = data.id
            data_json['label'] = data.title
            data_json['value'] = data.title

        if isinstance(data, Question):
            data_json['id'] = data.id
            data_json['label'] = data.title
            data_json['value'] = data.title

        results.append(data_json)

    return JsonResponse(results, safe=False)


# For autocomplete suggestions
@login_required
@ajax_required
def get_autocomplete_suggestions(request):
    querystring = request.GET.get('term', '')
    # Convert users, articles, questions objects into list to be
    # represented as a single list.
    users = list(User.objects.filter(
        Q(username__icontains=querystring) | Q(
            first_name__icontains=querystring) | Q(
                last_name__icontains=querystring)))
    articles = list(
        Article.objects.filter(Q(title__icontains=querystring) | Q(
            content__icontains=querystring), status='P'))
    questions = list(Question.objects.filter(
        Q(title__icontains=querystring) | Q(
            description__icontains=querystring)))
    # Add all the retrieved users, articles, questions to data_retrieved
    # list.
    data_retrieved = users
    data_retrieved.extend(articles)
    data_retrieved.extend(questions)
    results = []
    for data in data_retrieved:
        data_json = {}

        if isinstance(data, User):
            data_json['id'] = data.id
            data_json['label'] = data.username
            data_json['value'] = data.username

        if isinstance(data, Article):
            data_json['id'] = data.id
            data_json['label'] = data.title
            data_json['value'] = data.title

        if isinstance(data, Question):
            data_json['id'] = data.id
            data_json['label'] = data.title
            data_json['value'] = data.title

        results.append(data_json)

    final_suggestions = json.dumps(results)

    return HttpResponse(final_suggestions, 'application/json')
