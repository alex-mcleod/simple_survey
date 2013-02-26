from django import forms
from models import Survey, Question
from django.forms.formsets import formset_factory
import pdb

from django.forms.formsets import Form, BaseFormSet, formset_factory, \
        ValidationError

# Custom field which displays choice.value field instead of using choice.__unicode__ method when
# displaying choices in a form. 
class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.value

# Adapted from http://djangosnippets.org/snippets/1955/
class QuestionForm(Form):
    """Form for a single question on a survey"""
    def __init__(self, *args, **kwargs):
        # CODE TRICK #1
        # pass in a question from the formset
        # use the question to build the form
        # pop removes from dict, so we don't pass to the parent
        self.question = kwargs.pop('question')
        super(QuestionForm, self).__init__(*args, **kwargs)

        # CODE TRICK #2
        # add a non-declared field to fields
        # use an order_by clause if you care about order
        self.choices = self.question.choices.all(
                ).order_by('id')
        # TODO Allow empty label if question.required == False 
        self.fields['choices'] = CustomModelChoiceField(
                                                    queryset=self.choices, 
                                                    label=self.question.question, 
                                                    empty_label = None, 
                                                    widget = self.question.get_widget(),
                                                    )
        # You'd think this determines whether this question must be answered, but...
        self.required = self.question.required
        # This actually determines whether this question must be answered.
        self.empty_permitted = self.question.required

class BaseSurveySubmissionFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        # CODE TRICK #3 - same as #1:
        # pass in a valid survey object from the view
        # pop removes arg, so we don't pass to the parent
        self.survey = kwargs.pop('survey')

        # CODE TRICK #4
        # set length of extras based on query
        # each question will fill one 'extra' slot
        # use an order_by clause if you care about order
        self.questions = self.survey.questions.all().order_by('order')
        self.extra = len(self.questions)
        if not self.extra:
            raise Http404('No questions in survey.')
        # call the parent constructor to finish __init__  
        super(BaseSurveySubmissionFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, index, **kwargs):
        # CODE TRICK #5
        # know that _construct_form is where forms get added
        # we can take advantage of this fact to add our forms
        # add custom kwargs, using the index to retrieve a question
        # kwargs will be passed to our form class
        kwargs['question'] = self.questions[index]
        return super(BaseSurveySubmissionFormSet, self)._construct_form(index, **kwargs)

SurveySubmissionFormSet = formset_factory(
    QuestionForm, formset=BaseSurveySubmissionFormSet)

