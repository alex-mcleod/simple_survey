import models
from django.contrib import admin

class AnswerInline(admin.TabularInline):
   model = models.Submission.answers.through
   can_delete = False
   readonly_field = ['choice']
   #fields = ['question', 'answer']

class ChoiceInline(admin.StackedInline):
   model = models.Choice
   can_delete = False

class QuestionAdmin(admin.ModelAdmin): 
	fields = ['fieldname', 'question', 'help_text', 'required', 'widget']
	inlines = [ChoiceInline]

class QuestionInline(admin.StackedInline):
   model = models.Question

class SubmissionAdmin(admin.ModelAdmin):
	fields = ['user', 'survey']
	inlines = [AnswerInline] 

class SurveyAdmin(admin.ModelAdmin):
	fields = ['title', 'slug', 'description', 'is_active']
	prepopulated_fields = {"slug": ("title",)}
	inlines = [QuestionInline]

admin.site.register(models.Survey, SurveyAdmin)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Answer)
admin.site.register(models.Choice)
admin.site.register(models.Submission, SubmissionAdmin)