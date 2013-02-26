from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import inspect
import ast
from django.core.exceptions import ValidationError
import widgets
import renderers 

def list_from_module_classes(module):
    lst = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            lst.append( (str(name), str(name)) )
    return lst

def module_class_from_string(module, s):
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if str(name) == s:
                return obj 

WIDGETS = list_from_module_classes(widgets)

RENDERERS = list_from_module_classes(renderers)

class Survey(models.Model):
    def __unicode__(self):
        return "%s-%s" % (self.title, self.datetime)

    title = models.CharField(max_length = 200)
    slug = models.SlugField(unique=True)
    datetime = models.DateTimeField('creation date', auto_now_add = True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)

class Choice(models.Model):
    def __unicode__(self):
        return "%s-%s" % (self.question, self.value)

    question = models.ForeignKey('Question', related_name = 'choices', default = None)
    value = models.CharField(max_length = 200)
    models.DateTimeField('creation date', auto_now_add = True)

    # Return the value of this choice as an integer. 
    def value_as_int(self):
        # Try simply converting the value to an integer. 
        try:
            integer = int(self.value)
        except:
            integer = None
        # If that fails, use the position of this choice in it's parent question to determine integer. TODO
        # This is dangerous, if choices are deleted or added then this value becomes invalid. 
        if not integer:
            integer = 0
            for c in self.question.choices:
                if c == self:
                    break
                integer += 1
        return integer

class Question(models.Model):
    def __unicode__(self):
        return "%s" % (self.question)

    survey = models.ForeignKey(Survey, related_name="questions")
    datetime = models.DateTimeField('creation date', auto_now_add = True)
    fieldname = models.CharField(
        max_length=32,
        help_text=_('a single-word identifier used to track this value; '
                    'it must begin with a letter and may contain '
                    'alphanumerics and underscores (no spaces).'))
    question = models.TextField(help_text=_(
        "Appears on the survey entry page."))
    order = models.IntegerField(blank = False) 
    help_text = models.TextField(
        blank=True)
    required = models.BooleanField(
        default=False,
        help_text=_("Unsafe to change on live surveys. Radio button list and "
                    "drop down list questions will have a blank option if "
                    "they aren't required."))
    choices_text = models.TextField(
                                "choices", 
                                help_text = _("Add one choice per line. Leave this field blank if this is a free response question."), 
                                blank = True
                                )
    widget = models.CharField(max_length = 200, choices = WIDGETS, blank = False)
    renderer = models.CharField(max_length = 200, choices = RENDERERS, blank = True, null = True)
    html_attributes = models.CharField(max_length = 200, blank = True, help_text = _("HTML attributes must be written in the form of a Python dictionary."))

    def clean(self):
        if self.html_attributes != '':
            invalid = False
            try:
                html_attributes = ast.literal_eval(self.html_attributes)
            except:
                invalid = True
            if type(self.html_attributes) != dict:
                invalid = True
            if invalid:
                raise ValidationError('html_attributes is not formatted correctly.')

    def get_html_attributes(self):
        # literal_eval will fail if self.html_attributes is an empty string.
        try: 
            return ast.literal_eval(self.html_attributes)
        except:
            return None

    def save(self, *args, **kwargs):
        super(Question, self).save(*args, **kwargs) # Call the "real" save() method.
        for line in self.choices_text.splitlines():
            skip = False
            for choice in self.choices.all():
                if line == choice.value:
                    skip = True
            if not skip:
                c = Choice(question = self, value = line.strip())
                c.save()

    def get_widget(self, renderer = None):
        assert(self.id != None)
        obj = module_class_from_string(widgets, self.widget)
        attrs = self.html_attributes
        renderer = self.renderer
        # TODO This if statement makes no sense. Attrs and renderer are not connected. 
        if attrs and renderer:
            return obj(renderer = renderer, attrs = attrs) 
        else:
            return obj()

    def get_renderer(self):
        if self.renderer:
            renderer = module_class_from_string(renderers, self.renderer)
            return renderer
        return None

class Answer(models.Model):
    def __unicode__(self):
        return "%s-%s" % (self.question, self.choice)

    question = models.ForeignKey(Question)
    choice = models.ForeignKey(Choice)
    datetime = models.DateTimeField('creation date', auto_now_add = True)

class Submission(models.Model):
    def __unicode__(self):
        return "%s-%s" % (self.survey, self.datetime) 

    user = models.ForeignKey(User)
    datetime = models.DateTimeField('creation date', auto_now_add = True)
    survey = models.ForeignKey(Survey)
    answers = models.ManyToManyField(Answer, related_name = 'submission')