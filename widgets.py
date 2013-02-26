import django.forms.widgets
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

class TextInput(django.forms.widgets.TextInput):
	pass

class Textarea(django.forms.widgets.Textarea):
	pass

class CheckboxInput(django.forms.widgets.CheckboxInput):
	pass

class Select(django.forms.widgets.Select):
	pass

class RadioSelect(django.forms.widgets.RadioSelect):
	pass

# Cusom radio select which returns options inline using the bootstrap framework. 
class InlineRadioSelect(django.forms.widgets.RadioSelect):
	def render(self, name, value, attrs=None, choices=()):
		"""Outputs a <label> for this set of radio fields. get_renderer also adds label, so end up 
		with two sets of labels."""
		print "HERE!"
        	return mark_safe(u'\n'.join([u'<label class = "radio inline">%s</label>'
               % force_unicode(w) for w in self.get_renderer(name, value, attrs, choices)]))