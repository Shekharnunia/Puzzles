from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, CreateView

from helpers import AuthorRequiredMixin, TeacherRequiredMixin
from .models import Assignment


class AllAssignmentListView(LoginRequiredMixin, ListView):
	model = Assignment
	paginate_by = 10
	context_object_name = 'assignments'

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


class AssignmentDraftListView(AllAssignmentListView, AuthorRequiredMixin):

	def get_queryset(self):
		return Assignment.objects.get_draft_assignment()

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["active"] = "draft"
		return context


class TagAssignmentListView(AllAssignmentListView):
    """Overriding the original implementation to call the tag question
    list."""
    def get_queryset(self, **kwargs):
        return Assignment.objects.filter(tags__name=self.kwargs['tag_name'])


class AssignmentDetailView(LoginRequiredMixin, DetailView):
	model = Assignment
	context_object_name = 'assignment'


class AssignmentCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
	model = Assignment
	fields = ('topic', 'description', 'assignment_file', 'tags', 'draft',)
	template_name = 'assignment/assignment_create.html'
	message = ("Your Assignment has been created.")

	def form_valid(self, form):
		form.instance.uploader = self.request.user
		return super().form_valid(form)

	def get_success_url(self):
		messages.success(self.request, self.message)
		return reverse("assignment:all_list")


class AssignmentEditView(LoginRequiredMixin, TeacherRequiredMixin,  UpdateView):
	model = Assignment
	context_object_name = 'assignment'
	fields = ('topic', 'description', 'assignment_file', 'tags',)


class AssignmentDeleteView(LoginRequiredMixin, TeacherRequiredMixin, AuthorRequiredMixin, DeleteView):
	model = Assignment
	context_object_name = 'assignment'


class AssignmentDraftDetailView(LoginRequiredMixin, UpdateView):
	pass