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
