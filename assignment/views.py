from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import reverse, get_object_or_404, render, redirect
from django.views.generic import (
    ListView,
    DeleteView,
    UpdateView,
    DetailView,
    CreateView,
)

from helpers import AuthorRequiredMixin, TeacherRequiredMixin, StudentRequiredMixin
from .models import Assignment, StudentAssignment
from .forms import AssignmentForm, StudentAssignmentForm


class AllAssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    paginate_by = 10
    context_object_name = 'assignments'

    def get_queryset(self):
        return Assignment.objects.all().filter(uploader=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["popular_tags"] = Assignment.objects.get_counted_tags()
        context["active"] = "all"
        return context


class AssignmentListView(AllAssignmentListView):

    def get_queryset(self):
        return Assignment.objects.get_assignment()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "assignment"
        return context


class AssignmentDraftListView(AllAssignmentListView, TeacherRequiredMixin):

    def get_queryset(self):
        return Assignment.objects.get_draft_assignment().filter(uploader=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "draft"
        return context


class AssignmentOldestListView(AllAssignmentListView):

    def get_queryset(self):
        return Assignment.objects.get_oldest_student()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "oldest"
        return context


class AssignmentNewestListView(AllAssignmentListView):

    def get_queryset(self):
        return Assignment.objects.get_newest_student()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "newest"
        return context


class TagAssignmentListView(AllAssignmentListView):
    """Overriding the original implementation to call the tag question
    list."""

    def get_queryset(self, **kwargs):
        return Assignment.objects.filter(tags__name=self.kwargs['tag_name'])


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    context_object_name = 'assignment'

    def get_context_data(self, **kwargs):
        session_key = 'viewed_assignment_{}'.format(self.object.pk)
        if not self.request.session.get(session_key, False):
            self.object.assignment_views += 1
            self.object.save()
            self.request.session[session_key] = True
        return super().get_context_data(**kwargs)


@login_required
def assignment_detail_view(request, pk, slug):
    form = StudentAssignmentForm(request.POST, request.FILES)
    t_assignment = get_object_or_404(Assignment, pk=pk)
    session_key = 'viewed_assignment_{}'.format(t_assignment.pk)
    if not request.session.get(session_key, False):
        t_assignment.assignment_views += 1
        t_assignment.save()
        request.session[session_key] = True
    s_assignment = StudentAssignment.objects.filter(assignment=t_assignment)
    if request.method == 'POST':
        if form.is_valid() and request.user.is_student:
            s_assignment = form.save(commit=False)
            s_assignment.assignment = t_assignment
            s_assignment.user = request.user
            s_assignment = form.save()

            messages.success(request, 'assignment successfully submitted')
            return redirect(s_assignment.get_absolute_url())

            # subject = 'There is a assignment uploaded for your Question'
            # email_from = 'settings.EMAIL_HOST_USER'
            # recipient_list = [question.created_by.email, ]
            # message = "heloo"
            # context = {
            #     'question_user': question.created_by,
            #     'assignment_user': request.user,
            # }
            # context_message = get_template('assignment_mail.txt').render(context)
            # send_mail(subject,
            # context_message,
            # email_from,
            # recipient_list,
            # fail_silently=True)
    form = StudentAssignmentForm
    args = {
        'assignment': t_assignment,
        'form': form,
        's_assignments': s_assignment
    }
    return render(request, 'assignment/assignment_detail.html', args)


class StudentAssignmentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StudentAssignment
    form_class = StudentAssignmentForm
    template_name = 'assignment/edit_assignment.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'assignment'
    message = ("assignment successfully updated")

    def get_success_url(self):
        assignment = self.get_object()
        messages.success(self.request, self.message)
        return reverse('assignment:detail',
                       kwargs={'pk': assignment.assignment.pk,
                               'slug': assignment.assignment.slug})

    def test_func(self):
        assignment = self.get_object()
        if self.request.user == assignment.user:
            return True
        return False


class StudentAssignmentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    """Basic EditView implementation to edit existing articles."""
    model = StudentAssignment
    message = ("Your article has been deleted.")
    context_object_name = 'assignment'
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        assignment = self.get_object()
        messages.success(self.request, self.message)
        return reverse('assignment:detail',
                       kwargs={'pk': assignment.assignment.pk,
                               'slug': assignment.assignment.slug})


class AssignmentCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignment/assignment_create.html'
    message = ("Your Assignment has been created.")

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse("assignment:all_list")


class AssignmentEditView(LoginRequiredMixin, UserPassesTestMixin, TeacherRequiredMixin, UpdateView):
    model = Assignment
    context_object_name = 'assignment'
    fields = ('topic', 'description', 'assignment_file', 'tags',)
    message = ("assignment successfully updated")

    def get_success_url(self):
        assignment = self.get_object()
        messages.success(self.request, self.message)
        return reverse('assignment:detail',
                       kwargs={'pk': assignment.pk,
                               'slug': assignment.slug})


class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, TeacherRequiredMixin, DeleteView):
    model = Assignment
    context_object_name = 'assignment'
    message = ("Your article has been deleted.")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        assignment = self.get_object()
        messages.success(self.request, self.message)
        return reverse('assignment:detail',
                       kwargs={'pk': assignment.pk,
                               'slug': assignment.slug})

    def test_func(self):
        assignment = self.get_object()
        if self.request.user == assignment.uploader:
            return True
        return False
