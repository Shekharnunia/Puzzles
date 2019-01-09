from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, CreateView

from .models import Assignment


class AssignmentListView(ListView):
	model = Assignment
	paginated_by = 10
	context_object_name = 'assignments'


class AssignmentDetailView(DetailView):
	model = Assignment
	context_object_name = 'assignment'


class AssignmentCreateView(CreateView):
	model = Assignment
	fields = ('topic', 'description', 'assignment_file', 'tags',)
	template_name = 'assignment/assignment_create.html'
	success_url = '/'


class AssignmentEditView(UpdateView):
	model = Assignment
	context_object_name = 'assignment'
	fields = ('topic', 'description', 'assignment_file', 'tags',)


class AssignmentDeleteView(DeleteView):
	model = Assignment
	context_object_name = 'assignment'
