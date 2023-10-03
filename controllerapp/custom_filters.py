from django import template

register = template.Library()

@register.filter(name='format_date')
def format_date(value, format_str):
    return value.strftime(format_str)
