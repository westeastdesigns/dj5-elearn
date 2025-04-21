from django.contrib.auth.models import User
from django.db import models


# Course models. Data Structure = Subject/ Course/ Module/ Content (image|text|file|video)
class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    # owner is the instructor who created this course
    owner = models.ForeignKey(
        User,
        related_name='courses_created',
        on_delete=models.CASCADE
    )
    # subject is the subject this course belongs to. 
    # it's a ForeignKey field that points to the Subject model
    subject = models.ForeignKey(
        Subject,
        related_name='courses',
        on_delete=models.CASCADE
    )
    # title is the title of the course
    title = models.CharField(max_length=200)
    # slug is the slug for the course, useful in URLs 
    slug = models.SlugField(max_length=200, unique=True)
    # textfield column that stores an overview for the course
    overview = models.TextField()
    # creation date set automatically 
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course, related_name='modules', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
