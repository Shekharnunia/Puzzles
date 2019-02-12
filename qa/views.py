from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import get_template
from django.core.mail import send_mail, send_mass_mail

from helpers import ajax_required
from qa.models import Question, Answer
from qa.forms import QuestionForm, AnswerForm


# Done
class QuestionsIndexListView(LoginRequiredMixin, ListView):
    """CBV to render a list view with all the registered questions."""
    model = Question
    paginate_by = 10
    context_object_name = "questions"

    def get_queryset(self, **kwargs):
        return Question.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["popular_tags"] = Question.objects.get_counted_tags()
        context["active"] = "all"
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
        return Question.objects.get_answered()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "answered"
        return context


# Done
class QuestionListView(QuestionsIndexListView):
    """CBV to render a list view with all question which haven't been marked
    as answered."""

    def get_queryset(self, **kwargs):
        return Question.objects.get_unanswered()

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
    message = _("Your question has been Updated.")
    template_name = "qa/question_close_form.html"
    context_object_name = 'question'
    form_class = QuestionForm

    def form_valid(self, form):
        question = form.save(commit=False)
        question.close_question = self.request.user
        question.status = 'C'
        question.save(update_fields=["status", "close_question"])
        messages.success(self.request, 'Your question has been Updated.')
        return redirect(reverse("qa:index_noans"))

    def test_func(self):
        if self.request.user.is_teacher:
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
        form.instance.status = 'O'
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse("qa:index_noans")


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
        messages.success(self.request, self.message)
        return reverse("qa:index_noans")

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
class CreateAnswerView(LoginRequiredMixin, CreateView):
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
        subject = '[Puzzles.com] {}'.format(question.title)
        email_from = 'settings.EMAIL_HOST_USER'
        recipient_list = [question.user.email, ]
        message = "heloo"

        context = {
            'question_user': question.user,
            'answer_user': self.request.user,
            'url': question.get_absolute_url,
            'title': question.title,
            'content': question.content,
        }
        context_message = get_template('email/answer_mail.txt').render(context)

        send_mail(subject, context_message, email_from, recipient_list, fail_silently=True)

        subject = '[Puzzles.com] {}'.format(question.title)
        email_from = 'settings.EMAIL_HOST_USER'

        a = set()
        for x in question.answer_set.all():
            a.add(x.user.email)

        recipient_list = []
        for i in a:
            recipient_list.append(i)
        message = "heloo"
        context = {
            'url': question.get_absolute_url,
            'title': question.title,
            'content': question.content,
        }

        context_message = get_template('email/answer_uploader_mail.txt').render(context)
        send_mail(subject, context_message, email_from, recipient_list, fail_silently=True)
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse(
            "qa:index_all")


# Done
class EditAnswerView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Answer
    message = _("Your Answer has been updated.")
    context_object_name = 'answer'
    fields = ["content", ]
    pk_url_kwarg = 'answer_id'
    template_name = 'qa/answer_edit_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse("qa:question_detail", kwargs={"pk": self.kwargs["pk"], "slug": self.kwargs["slug"]})

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
        messages.success(self.request, self.message)
        return reverse("qa:question_detail", kwargs={"pk": self.kwargs["pk"], "slug": self.kwargs["slug"]})

    def test_func(self):
        answer = self.get_object()
        if self.request.user == answer.user:
            return True
        return False


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
