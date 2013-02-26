from django.template import RequestContext, loader
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from models import Survey, Submission, Answer
from forms import SurveySubmissionFormSet

def submit_survey(user, survey, submission_data):
    formset = SurveySubmissionFormSet(survey=survey, data=submission_data)
    submission = None
    if formset.is_valid():
        submission = Submission.objects.create(user = user, survey = survey)
        for form in formset.forms:
            for k in form.cleaned_data:
                choice = form.cleaned_data[k]
                a = Answer.objects.get_or_create(question = choice.question, choice = choice)
                submission.answers.add(a[0])
        submission.save()
    return {'submission' : submission, 'formset' : formset}

@login_required
def take_survey(request, survey_slug):
    try:
    	survey = Survey.objects.get(slug=survey_slug)
    except Survey.DoesNotExist:
        return Http404('Invalid survey.')
    next = request.GET.get('next', '')
    store_in_session = request.GET.get('store_in_session', '')
    if request.method == 'POST':
        submission = submit_survey(request.user, survey, request.POST)
        formset = submission['formset']
        if submission['formset'].is_valid():
                # Next should always be in request.POST. It may be an emptry string though, in which case
                # take_survey view is simply reloaded. 
                next = request.POST.get('next', '')
                store_in_session = request.POST.get('store_in_session', '')
                if store_in_session == 'True':
                    request.session['survey_submission'] = submission['submission']
                if next != '':
                    return redirect(next)
    else:
        formset = SurveySubmissionFormSet(survey=survey)
    t = loader.get_template('simple_survey/take_survey.html')
    c = RequestContext(request, {
                            'survey': survey, 
                            'formset': formset, 
                            'next' : next, 
                            'store_in_session' : store_in_session
                            })
    return HttpResponse(t.render(c))