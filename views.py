from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, FileResponse
from .NBA_Beautiful_Data.analytics import analytics_API as Api
import logging
from .models import Graph
import numpy as np
import shutil
import os
from collections import OrderedDict
import datetime
from sendfile import sendfile
from .constants import Defaults as Vars
from .constants import ScatterFilters as sf


# VIEWS
def index(request):
    # can provide optional 3rd arg of dictionary to pass to template
    return render(request, 'analyze/index.html', {})


def download_plot_png(request):
    print('\nIN DOWNLOAD VIEW')
    graph = get_object_or_404(Graph, pk=1)
    path = graph.create_png_location()

    return sendfile(request, path, attachment=True, attachment_filename='view.png')


def plot(request):
    """
    The plotting view for the NBA data set.

    :param request: HTML request object
    :return: The html page
    """
    print('\nIN PLOT VIEW')

    d = os.path.dirname(os.path.abspath(__file__))
    location = os.path.join(d, 'Media', 'Plots')
    for f in os.listdir(location):
        f_path = os.path.join(location, f)
        if os.path.getmtime(f_path) > 30:
            os.remove(f_path)
    # todo, need to user post/redirect/get pattern to avoid refresh causing new entry
    if request.method == 'POST' and 'filter_submit' in request.POST:
        # create graph object from post request
        template_dict = {
            'selected_x_key': request.POST.get('x_key_name', default=Vars.x_key),
            'selected_y_key': request.POST.get('y_key_name', default=Vars.y_key),
            'selected_team_name': request.POST.get('team_name', default=Vars.team),
            'grid_enable': request.POST.get('grid_enable', default=Vars.grid),
            'trend_enable': request.POST.get('trend_enable', default=Vars.trend),
            'selected_min_seconds': request.POST.get('min_seconds', default=Vars.min_seconds),
            'selected_max_seconds': request.POST.get('max_seconds', default=Vars.max_seconds),
        }
        # check each separately so the other will persist if one is not a valid int
        try:
            template_dict['selected_min_seconds'] = int(template_dict['selected_min_seconds'])
        except ValueError:
            template_dict['selected_min_seconds'] = 0
        try:
            template_dict['selected_max_seconds'] = int(template_dict['selected_max_seconds'])
        except ValueError:
            template_dict['selected_max_seconds'] = 100 * 60
        grid_pk = 0 if template_dict['grid_enable'] == 'Enable' else 1
        trend_pk = 0 if template_dict['trend_enable'] == 'Enable' else 1
        graph = Graph(x_key=template_dict['selected_x_key'],
                      y_key=template_dict['selected_y_key'],
                      team=template_dict['selected_team_name'],
                      trend_line=sf.trend_choices[trend_pk],
                      grid=sf.grid_choices[grid_pk],
                      min_seconds=template_dict['selected_min_seconds'],
                      max_seconds=template_dict['selected_max_seconds'],)
        graph.save()
    else:
        # create default object
        graph = Graph(x_key=Vars.x_key,
                      y_key=Vars.y_key,
                      team=Vars.team,
                      trend_line=Vars.trend,
                      grid=Vars.grid)

    outlier_dict = graph.get_outlier_dict()

    # dict that is passed to the html template file
    svg_dict = {
        'outlier_dict': outlier_dict,
        'graph': graph,
        'y_keys': sf.y_keys,
        'x_keys': sf.x_keys,
        'teams': sf.teams,
        'grid_choices': sf.grid_choices,
        'trend_choices': sf.trend_choices,
    }  # set the plot data

    return render(request, 'analyze/plot.html', svg_dict)
