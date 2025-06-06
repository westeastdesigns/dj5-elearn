from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import ModuleFormSet
from .models import Course


# Mixins allow common behavior for multiple course views.
class OwnerMixin:
    """ implements the get_queryset() method used by the views to get the base QuerySet

    Returns:
        QuerySet[ListView]: retrieves only courses created by the current user
    """
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    """ implements the form_valid() method used by views that use Django's ModelFormMixin with forms or model forms including CreateView and UpdateView. Executes when form is valid, saving current user as owner of the object being saved
    """
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    """OwnerCourseMixin inherits OwnerMixin, LoginRequiredMixin, and PermissionRequiredMixin; and provides model, fields, and success_url

    Args:
        OwnerMixin (mixin): class being inherited, provides QuerySet
        model (model): model used for QuerySets, this is used by all views
        fields (list): fields of the model to build the model form of CreateView and UpdateView views
        success_url (str): URL used by CreateView, UpdateView, and DeleteView to redirect user after successfully submitting form or the object is deleted
    """
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """OwnerCourseEditMixin adds the template_name attribute

    Args:
        OwnerCourseMixin (mixin): class being inherited, also inherits from OwnerMixin
        OwnerEditMixin (mixin): class being inherited, validates forms with form_valid()
    """
    template_name = 'courses/manage/course/form.html'
    

# Class-based views to create, edit, and delete courses.
class ManageCourseListView(OwnerCourseMixin, ListView):
    """ManageCourseListView is a class-based view that inherits from OwnerCourseMixin and Django's ListView, with the get_queryset() method overridden to retrieve only courses created by the current user.

    Args:
        ListView (view): Django's generic ListView
    """
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """CourseCreateView uses a model form to create a new Course object. Uses fields defined in OwnerCourseMixin to build a model form and also subclasses CreateView

    Args:
        OwnerCourseEditMixin (mixin): defines the template
        CreateView (view): CourseCreateView subclasses Django's generic CreateView
    """
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    """CourseUpdateView allows the editing of an existing Course object. Uses fields defined in OwnerCourseMixinto build a model form and subclasses UpdateView

    Args:
        OwnerCourseEditMixin (mixin): defines the template
        UpdateView (view): CourseUpdateView subclasses Django's generic UpdateView
    """
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """CourseDeleteView defines a specific template_name for a template to confirm course deletion. Inherits from OwnerCourseMixin and the Django generic DeleteView

    Args:
        OwnerCourseMixin (mixin): class being inherited, also inherits from CourseMixin
        DeleteView (view): CourseDeleteView inherits from Django's generic DeleteView
    """
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)
    
    def dispatch(self, request, pk):
        self.course = get_object_or_404(
            Course, id=pk, owner=request.user
        )
        return super().dispatch(request, pk)
    
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {'course': self.course, 'formset': formset}
        )

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response(
            {'course': self.course, 'formset': formset}
        )
    