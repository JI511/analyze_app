import datetime

from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    """
    index a list or dictionary at a given value
    """
    return indexable[i]


@register.filter
def available_pages(my_dict, i):
    """
    Returns the keys of a dictionary
    """
    my_keys = []
    print(type(my_dict))
    if isinstance(my_dict, dict):
        [my_keys.append(key) for key in my_dict.keys() if key != i]
    return my_keys


@register.filter
def check_current_page(page, current_page):
    """
    Checks if a page is the same as the current page.
    """
    return int(page) == int(current_page)


@register.filter
def convert_date(date_obj):
    """
    Converts a datetime.date or datetime.datetime object into a human readable date.
    """
    if isinstance(date_obj, (datetime.date, datetime.datetime)):
        return date_obj.strftime('%A, %B %d')
