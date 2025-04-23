from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


# Course models. Data Structure = Subject/ Course/ Module/ Content (image|text|file|video)
class Subject(models.Model):
    """Subject model describes a general topic under which a course can be included.

    Args:
        models 
        title (CharField): title of the topic
        slug (SlugField): slug for the subject, useful in URLs

    Returns:
        str: title
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    """Course model describes a course created by its owner, the instructor of that course.

    Args:
        models 
        owner (ForeignKey): owner is the instructor who created this course
        subject (ForeignKey): the subject this course belongs to. it's a ForeignKey field that points to the Subject model
        title (CharField): title is the title of the course
        slug (SlugField): slug is the slug for the course, useful in URLs 
        overview (TextField): textfield column that stores an overview for the course
        created (DateTimeField): creation date set automatically 


    Returns:
        str: title
    """
    owner = models.ForeignKey(
        User,
        related_name='courses_created',
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        related_name='courses',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.title


class Module(models.Model):
    """Module model describes a section within a course, containing content related to that portion of the course.

    Args:
        models 
        course (ForeignKey): links to the course the module is related to
        title (CharField): the title of the module
        description (TextField): a text description of the module

    Returns:
        str: title
    """
    course = models.ForeignKey(
        Course, 
        related_name='modules', 
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Content(models.Model):
    """Content represents the modules contents and defines a generic relation to associate any object with the content object.

    Args:
        models 
        module (ForeignKey): a module contains multiple contents, ForeignKey points to Module model
        content_type (ForeignKey): ForeignKey points to ContentType model
        object_id (PositiveIntegerField): stores primary key of the related object
        
        item (GenericForeignKey): GenericForeignKey field to the related object combining the two previous fields 
    """
    module = models.ForeignKey(
        Module,
        related_name='contents',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    