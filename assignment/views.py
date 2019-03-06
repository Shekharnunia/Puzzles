from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import get_template
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from comments.forms import CommentForm
from comments.models import Comment
from helpers import AuthorRequiredMixin, TeacherRequiredMixin

from .forms import AssignmentForm, StudentAssignmentForm
from .models import Assignment, StudentAssignment


class AllAssignmentListView(LoginRequiredMixin, ListView):
    """ View to get all the assignment of a particluar 
    user which can be in draft or not"""

    model = Assignment
    paginate_by = 10
    context_object_name = 'assignments'

    def get_queryset(self):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            return Assignment.objects.search(query)
        else:
            assignemt = Assignment.objects.get_assignment()
            all_assignemt = Assignment.objects.filter(uploader=self.request.user)
            union = all_assignemt.union(assignemt).order_by('-timestamp')
            return union

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_student:
            context["active"] = "newest"
        else:
            context["active"] = "all"
        context['nbar'] = 't_assignment_nav'
        if self.request.GET.get("query"):
            context['search'] = True
            query = self.request.GET.get("query")
            context["extra"] = '&query={}'.format(query)
            anssignment = self.object_list
            context['assignment_count'] = anssignment.count()
            return context
        context["popular_tags"] = Assignment.objects.get_counted_tags()
        context['search_url'] = reverse('assignment:all_list')
        return context


class AssignmentListView(AllAssignmentListView):
    """ View to get all the assignment of all the
    user which are not in draft or open to see"""

    def get_queryset(self):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            return Assignment.objects.get_assignment().search(query)
        else:
            return Assignment.objects.get_assignment().order_by('-timestamp')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_student:
            context["active"] = "newest"
        else:
            context["active"] = "assignment"
        return context


class AssignmentDraftListView(TeacherRequiredMixin, AllAssignmentListView):
    """ View to get all the assignment of a particular
    user which are in draft"""

    def get_queryset(self):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            request = self.request
            return Assignment.objects.draft_search(query, request)
        else:
            request = self.request
            return Assignment.objects.get_draft_assignment(request)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "draft"
        return context


class AssignmentOldestListView(AllAssignmentListView):
    """ View to get all the assignment in a oldest 
    order which can be seen by students"""

    def get_queryset(self):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            return Assignment.objects.get_oldest_student().search(query)
        else:
            return Assignment.objects.get_oldest_student()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "oldest"
        return context


class AssignmentNewestListView(AllAssignmentListView):
    """ View to get all the assignment in a newest
    order which can be seen by students"""

    def get_queryset(self):
        if self.request.GET.get("query"):
            query = self.request.GET.get("query")
            return Assignment.objects.search(query)
        else:
            return Assignment.objects.get_newest_student()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = "newest"
        return context


class TagAssignmentListView(AllAssignmentListView):
    """Overriding the original implementation to call the tag question
    list."""

    def get_queryset(self, **kwargs):
        return Assignment.objects.filter(draft=False).filter(
            tags__name=self.kwargs['tag_name']).order_by('-timestamp')


class AssignmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Assignment
    context_object_name = 'assignment'

    def get_context_data(self, **kwargs):
        session_key = 'viewed_assignment_{}'.format(self.object.pk)
        if not self.request.session.get(session_key, False):
            self.object.assignment_views += 1
            self.object.save()
            self.request.session[session_key] = True
        return super().get_context_data(**kwargs)

    def test_func(self):
        assignment = self.get_object()
        if self.request.user == assignment.user or blog.draft == False:
            return True
        return False


@login_required
def assignment_detail_view(request, pk, slug):
    t_assignment = get_object_or_404(Assignment, pk=pk)
    if request.user == t_assignment.uploader or t_assignment.draft == False:
        session_key = 'viewed_assignment_{}'.format(t_assignment.pk)
        if not request.session.get(session_key, False):
            t_assignment.assignment_views += 1
            t_assignment.save()
            request.session[session_key] = True
        if request.user.is_student == True:
            s_assignment = StudentAssignment.objects.filter(assignment=t_assignment).filter(user=request.user).order_by('-timestamp')
        elif request.user.is_teacher and t_assignment.uploader == request.user:
            s_assignment = StudentAssignment.objects.filter(assignment=t_assignment).order_by('-timestamp')
        else:
            s_assignment = None

        initial_data = {
            "content_type": t_assignment.get_content_type,
            "object_id": t_assignment.id
        }

        if request.method == 'POST':
            form = StudentAssignmentForm(request.POST, request.FILES)
            if form.is_valid() and request.user.is_student:
                s_assignment = form.save(commit=False)
                s_assignment.assignment = t_assignment
                s_assignment.user = request.user
                s_assignment = form.save()

                subject = '{} uploaded an assignment solution'.format(s_assignment.user)
                email_from = 'settings.EMAIL_HOST_USER'
                recipient_list = [t_assignment.uploader.email, ]

                current_site = get_current_site(request)
                context = {
                    'assignment_user': t_assignment.uploader,
                    'solution_uploader_user': request.user,
                    'url': t_assignment.get_absolute_url,
                    'domain': current_site.domain,
                    'title': t_assignment.topic,
                }
                context_message = get_template('email/assignment_mail.txt').render(context)

                send_mail(subject, context_message, email_from, recipient_list, fail_silently=True)

                messages.success(request, 'assignment successfully submitted')
                return redirect(s_assignment.get_absolute_url())
            else:
                messages.warning(request, 'Form containing error')

        form = StudentAssignmentForm()
        comment_form = CommentForm(initial=initial_data)
        comments = t_assignment.comments
        args = {
            'assignment': t_assignment,
            's_form': form,
            's_assignments': s_assignment,
            "comments": comments,
            "comment_form": comment_form,
        }
        return render(request, 'assignment/assignment_detail.html', args)
    else:
        raise PermissionDenied


def comment(request, slug, pk):
    if request.method == 'POST':
        t_assignment = get_object_or_404(Assignment, pk=pk)

        initial_data = {
            "content_type": t_assignment.get_content_type,
            "object_id": t_assignment.id
        }
        comment_form = CommentForm(request.POST or None, initial=initial_data)

        if comment_form.is_valid():
            c_type = comment_form.cleaned_data.get("content_type")
            content_type = ContentType.objects.get(model=c_type)
            obj_id = comment_form.cleaned_data.get('object_id')
            content_data = comment_form.cleaned_data.get("content")
            parent_obj = None
            try:
                parent_id = int(request.POST.get("parent_id"))
            except:
                parent_id = None

            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    parent_obj = parent_qs.first()

            new_comment, created = Comment.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=obj_id,
                content=content_data,
                parent=parent_obj,
            )
            messages.success(request, 'comment successfully submitted')
            return redirect(new_comment.content_object.get_absolute_url())
        else:
            messages.warning(request, 'Form containing error')
            return redirect(t_assignment.get_absolute_url())


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


class AssignmentEditView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Assignment
    context_object_name = 'assignment'
    fields = ('topic', 'description', 'assignment_file', 'draft', 'tags')
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
        messages.success(self.request, self.message)
        return reverse('assignment:list')

    def test_func(self):
        assignment = self.get_object()
        if self.request.user == assignment.uploader:
            return True
        return False
