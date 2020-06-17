from django import template

register = template.Library()


@register.filter
def add_image(pre_path, app_name):
    """
    index a list or dictionary at a given value
    """
    app_names = {'analyze': 'nba_header.png',
                 'houseplants': 'houseplant_header.png',
                 'stocks': 'nba_header.png', }
    return pre_path + app_names[app_name]
