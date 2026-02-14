from django import template
from django.template.loader import get_template

register = template.Library()


@register.filter
def get_step_title(step, step_titles):
    # Ensure that 'step' is an integer or set a default
    step = int(step) if step is not None else 0
    return step_titles[step] if step < len(step_titles) else step_titles[0]


@register.filter
def range_filter(value):
    return range(value)

@register.filter
def index(sequence, position):
    """
    Custom template filter to get an item from a list by index.
    """
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return ""
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)



@register.filter
def div(value, arg):
    return value / arg

@register.filter
def multiply(value, arg):
    return value * arg


