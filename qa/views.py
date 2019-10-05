from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.utils import IntegrityError
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from helpers import ajax_required
from qa.forms import AnswerForm, QuestionCloseForm, QuestionForm
from qa.models import Answer, Question


# Done
class QuestionsIndexListView(LoginRequiredMixin, ListView):
    """CBV to render a list view with all the registered questions."""
    model = Question
    paginate_by = 10
    context_object_name = "questions"

    def get_queryset(self, *args, **kwargs):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            return Question.objects.search(query)
        else:
            return Question.objects.all().select_related("user").order_by("-timestamp").prefetch_related("tagged_items__tag", "answer_set")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "all"
        context['nbar'] = 'qa_nav'
        if self.request.GET.get("query"):
            context['search'] = True
            query = self.request.GET.get("query")
            context["extra"] = '&query={}'.format(query)
            question = self.object_list
            context['question_count'] = question.count()
            return context
        context["popular_tags"] = Question.objects.get_counted_tags()
        context["search_url"] = reverse('qa:index_all')
        return context


# Done
class TagQuestionListView(QuestionsIndexListView):
    """Overriding the original implementation to call the tag question
    list."""

    def get_queryset(self, **kwargs):
        return Question.objects.filter(tags__name=self.kwargs['tag_name']).exclude(status='D').order_by('-total_votes')


# Done
class QuestionAnsListView(QuestionsIndexListView):
    """CBV to render a list view with all question which have been already
    marked as answered."""

    def get_queryset(self, **kwargs):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            return Question.objects.get_answered().search(query)
        else:
            return Question.objects.get_answered().order_by('-pk')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "answered"
        return context


# Done
class QuestionListView(QuestionsIndexListView):
    """CBV to render a list view with all question which haven't been marked
    as answered."""

    def get_queryset(self, **kwargs):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            return Question.objects.get_unanswered().search(query)
        else:
            return Question.objects.get_unanswered().order_by('-pk')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "unanswered"
        return context


# Done
class QuestionDetailView(LoginRequiredMixin, DetailView):
    """View to call a given Question object and to render all the details about
    that Question."""
    model = Question
    context_object_name = "question"

    def get_context_data(self, **kwargs):
        session_key = 'viewed_question_{}'.format(self.object.pk)
        if not self.request.session.get(session_key, False):
            self.object.question_views += 1
            self.object.save()
            self.request.session[session_key] = True
        return super().get_context_data(**kwargs)


# Done
class QuestionDetaiCloseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    template_name = "qa/question_close_form.html"
    form_class = QuestionCloseForm
    context_object_name = 'question'

    def form_valid(self, form):
        question = form.save(commit=False)
        question.close_question_user = self.request.user
        question.status = 'C'
        question.close_question_date = timezone.now()
        question.save(update_fields=["status", "close_question_user", 'close_question_date', 'close_question_reason'])
        messages.success(self.request, "This question has been Closed.")
        return redirect(reverse("qa:index_noans"))

    def test_func(self):
        question = self.get_object()
        if (self.request.user.is_teacher and question.status == 'O') or self.request.user == question.user:
            return True
        return False


# Done
class CreateQuestionView(LoginRequiredMixin, CreateView):
    """
    View to handle the creation of a new question
    """
    form_class = QuestionForm
    template_name = "qa/question_form.html"
    message = _("Your question has been created.")

    def form_valid(self, form):
        question = form.save(commit=False)
        question.status = 'O'
        question.user = self.request.user
        question.save()
        form.save_m2m()
        messages.success(self.request, self.message)
        return redirect(question.get_absolute_url())


# Done
class EditQuestionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = "qa/question_edit_form.html"
    message = _("Your question has been Updated.")
    context_object_name = 'question'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        question = self.get_object()
        messages.success(self.request, self.message)
        return question.get_absolute_url()

    def test_func(self):
        question = self.get_object()
        if self.request.user == question.user:
            return True
        return False


# Done
class DeleteQuestionView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Question
    message = _("Your question has been Deleted.")
    context_object_name = 'question'

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse("qa:index_noans")

    def test_func(self):
        question = self.get_object()
        if self.request.user == question.user:
            return True
        return False


# Done
class CreateAnswerView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    View to create new answers for a given question
    """
    model = Answer
    form_class = AnswerForm
    message = _("Thank you! Your answer has been posted.")
    template_name = 'qa/answer_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs["question_id"]
        question = get_object_or_404(Question, pk=form.instance.question_id)
        question.other_user_receive_email.add(self.request.user)
        current_site = get_current_site(self.request)

        if not question.user == form.instance.user and question.receive_email == True:
            subject = '{}'.format(question.title)
            email_from = 'settings.EMAIL_HOST_USER'
            recipient_list = [question.user.email, ]
            current_site = get_current_site(self.request)
            context = {
                'question_user': question.user,
                'answer_user': self.request.user,
                'url': question.get_absolute_url,
                'domain': current_site.domain,
                'title': question.title,
                'content': question.get_markdown(),
            }
            context_message = get_template('email/answer_mail.txt').render(context)
            message = EmailMultiAlternatives(subject=subject, body=context_message, from_email=email_from, to=recipient_list)
            html_template = get_template('email/answer_mail.html').render(context)
            message.attach_alternative(html_template, "text/html")
            message.send()

        subject = '{}'.format(question.title)
        email_from = 'settings.EMAIL_HOST_USER'

        a = set()
        for x in question.other_user_receive_email.all():
            if not x == question.user and not self.request.user == x:
                a.add(x.email)

        recipient_list = []
        for i in a:
            recipient_list.append(i)
        context = {
            'url': question.get_absolute_url,
            'title': question.title,
            'domain': current_site.domain,
            'content': question.get_markdown(),
        }

        context_message = get_template('email/answer_uploader_mail.txt').render(context)
        message = EmailMultiAlternatives(subject=subject, body=context_message, from_email=email_from, to=recipient_list)
        html_template = get_template('email/answer_uploader_mail.html').render(context)
        message.attach_alternative(html_template, "text/html")
        message.send()
        return super().form_valid(form)

    def get_success_url(self):
        question_id = self.kwargs["question_id"]
        question = get_object_or_404(Question, pk=question_id)
        messages.success(self.request, self.message)
        return question.get_absolute_url()

    def test_func(self):
        question_id = self.kwargs["question_id"]
        question = get_object_or_404(Question, pk=question_id)
        if not question.status == 'C':
            return True
        return False


@login_required
@ajax_required
def receive_answer_email(request):
    question = get_object_or_404(Question, id=request.POST.get('id'))
    is_subscribed = False
    if question.other_user_receive_email.filter(id=request.user.id).exists():
        question.other_user_receive_email.remove(request.user)
        is_subscribed = False
    else:
        question.other_user_receive_email.add(request.user)
        is_subscribed = True
    context = {
        'question': question,
        'is_subscribed': is_subscribed,
    }
    if request.is_ajax():
        html = render_to_string('qa/subscribe_section.html', context, request=request)
        return JsonResponse({'form': html})


# Done
class EditAnswerView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Answer
    message = _("Your Answer has been updated.")
    context_object_name = 'answer'
    form_class = AnswerForm
    pk_url_kwarg = 'answer_id'
    template_name = 'qa/answer_edit_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        question_id = self.kwargs["pk"]
        question = get_object_or_404(Question, pk=question_id)
        messages.success(self.request, self.message)
        return question.get_absolute_url()

    def test_func(self):
        answer = self.get_object()
        if self.request.user == answer.user:
            return True
        return False


# Done
class DeleteAnswerView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Answer
    message = _("Your Answer has been Deleted.")
    context_object_name = 'answer'
    pk_url_kwarg = 'answer_id'

    def get_success_url(self):
        question_id = self.kwargs["pk"]
        question = get_object_or_404(Question, pk=question_id)
        messages.success(self.request, self.message)
        return question.get_absolute_url()

    def test_func(self):
        answer = self.get_object()
        if self.request.user == answer.user:
            return True
        return False


@login_required
def q_flag(request, pk, slug):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'GET':
        return render(request, 'qa/flag_question.html', {'question': question})
    if request.method == 'POST':
        if request.user in question.flag.all():
            messages.warning(request, 'You already flag this question')
            return redirect(question.get_absolute_url())
        question.flag.add(request.user)
        messages.success(request, 'You request for flag has been considered for this question')
        subject = 'Question has been flaged'
        email_from = 'settings.EMAIL_HOST_USER'
        recipient_list = [mail_tuple[1] for mail_tuple in settings.MANAGERS]
        message = "A question has been flaged"

        current_site = get_current_site(request)
        context = {
            'title': question.title,
            'content': question.content,
            'url': question.get_absolute_url,
            'domain': current_site.domain,
        }
        context_message = get_template('email/flag_question.txt').render(context)

        send_mail(subject, context_message, email_from, recipient_list, fail_silently=True)
        return redirect(question.get_absolute_url())


@login_required
def a_flag(request, pk, slug, answer_id):
    question = get_object_or_404(Question, pk=pk)
    answer = Answer.objects.get(uuid_id=answer_id)
    if request.method == 'GET':
        return render(request, 'qa/flag_answer.html', {'question': question, 'answer': answer})
    if request.method == 'POST':
        if request.user in answer.flag.all():
            messages.warning(request, 'You already flag this answer')
            return redirect(question.get_absolute_url())
        answer.flag.add(request.user)
        messages.success(request, 'You request for flag has been considered for this answer')
        subject = 'An answer has been flaged'
        email_from = 'settings.EMAIL_HOST_USER'
        recipient_list = [mail_tuple[1] for mail_tuple in settings.MANAGERS]
        message = "A question has been flaged"

        current_site = get_current_site(request)
        context = {
            'title': question.title,
            'content': answer.content,
            'url': question.get_absolute_url,
            'domain': current_site.domain,
        }
        context_message = get_template('email/flag_answer.txt').render(context)

        send_mail(subject, context_message, email_from, recipient_list, fail_silently=True)
        return redirect(question.get_absolute_url())


@login_required
@ajax_required
def question_vote(request):
    """Function view to receive AJAX call, returns the count of votes a given
    question has recieved."""
    if request.method == "POST":
        question_id = request.POST["question"]
        value = None
        if request.POST["value"] == "U":
            value = True

        else:
            value = False

        question = Question.objects.get(pk=question_id)
        try:
            question.votes.update_or_create(
                user=request.user, defaults={"value": value}, )
            question.count_votes()
            return JsonResponse({"votes": question.total_votes})

        except IntegrityError:
            return JsonResponse({'status': 'false',
                                 'message': _("Database integrity error.")},
                                status=500)

    else:
        return HttpResponseBadRequest(content=_("Wrong request type."))


@login_required
@ajax_required
def answer_vote(request):
    """Function view to receive AJAX call, returns the count of votes a given
    answer has recieved."""
    if request.method == "POST":
        answer_id = request.POST["answer"]
        value = None
        if request.POST["value"] == "U":
            value = True

        else:
            value = False

        answer = Answer.objects.get(uuid_id=answer_id)
        try:
            answer.votes.update_or_create(
                user=request.user, defaults={"value": value}, )
            answer.count_votes()
            return JsonResponse({"votes": answer.total_votes})

        except IntegrityError:
            return JsonResponse({'status': 'false',
                                 'message': _("Database integrity error.")},
                                status=500)

    else:
        return HttpResponseBadRequest(content=_("Wrong request type."))


# Done
@login_required
@ajax_required
def accept_answer(request):
    """Function view to receive AJAX call, marks as accepted a given answer for
    an also provided question."""
    if request.method == "POST":
        answer_id = request.POST["answer"]
        answer = Answer.objects.get(uuid_id=answer_id)
        answer.accept_answer()
        return JsonResponse({'status': 'true'}, status=200)

    else:
        return HttpResponseBadRequest(content=_("Wrong request type."))
