from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .fields import OrderField


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
        order (OrderField): ordering is calculated with respect to the course

    Returns:
        str: order and title
    """
    course = models.ForeignKey(
        Course, 
        related_name='modules', 
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Content(models.Model):
    """Content represents the modules contents and defines a generic relation to associate any object with the content object.

    Args:
        models 
        module (ForeignKey): a module contains multiple contents, ForeignKey points to Module model
        content_type (ForeignKey): ForeignKey points to ContentType model. Limited ContentType objects to text, video, image, and file
        object_id (PositiveIntegerField): stores primary key of the related object
        item (GenericForeignKey): GenericForeignKey field to the related object combining the two previous fields
        order (OrderField): order is calculated with respect to the module field 
    """
    module = models.ForeignKey(
        Module,
        related_name='contents',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in':('text', 'video', 'image', 'file')
        }
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    """ItemBase is an abstract model defining the owner, title, created, and updated fields. All types of content use these common fields.

    Args:
        models 
        owner (ForeignKey): stores which user created the content, with a different related_name auto-generated for each sub-model
        title (CharField): title of content
        created (DateTimeField): automatically generated date and time the content was created
        updated (DateTimeField): automatically generated date and time of most recent update to content

    Returns:
        str: title
    """
    owner = models.ForeignKey(
        User,
        related_name='%(class)s_related',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

class Text(ItemBase):
    """Text inherits from abstract model ItemBase, stores text content

    Args:
        ItemBase (TextField): text content
    """
    content = models.TextField()

class File(ItemBase):
    """File inherits from abstract model ItemBase, stores files such as PDFs. Does not include image or video files.

    Args:
        ItemBase (FileField): file content, for example: a PDF
    """
    file = models.FileField(upload_to='files')

class Image(ItemBase):
    """Image inherits from abstract model ItemBase, stores image files

    Args:
        ItemBase (FileField): image files, for example: a PNG
    """
    file = models.FileField(upload_to='images')

class Video(ItemBase):
    """Video inherits from abstract model ItemBase, stores videos. Uses URLField to provide a video URL for embedding

    Args:
        ItemBase (URLField): provides a video URL in order to embed it
    """
    url = models.URLField()