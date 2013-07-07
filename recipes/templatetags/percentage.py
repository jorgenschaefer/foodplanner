from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def percentage(value):
    return "{:.1f}%".format(float(value) * 100)
