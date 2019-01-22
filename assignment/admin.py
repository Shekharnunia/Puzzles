from django.contrib import admin

from .models import Assignment, StudentAssignment

admin.site.register(Assignment)

admin.site.register(StudentAssignment)
