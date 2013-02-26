import django.forms.widgets

class BootstrapRadioFieldRenderer(django.forms.widgets.RadioFieldRenderer):
	def render(self):
		"""Outputs a <label> for this set of radio fields."""
        	return mark_safe(u'\n'.join([u'<label class = "radio inline">%s</label>'
                % force_unicode(w) for w in self]))