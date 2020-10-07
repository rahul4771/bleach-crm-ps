from num2words import num2words
from django import template
register = template.Library()

@register.simple_tag()
def num_to_words(digit, *args, **kwargs):
    digit_to_words = num2words(digit).upper()
    return digit_to_words