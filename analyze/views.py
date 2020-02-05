from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, FileResponse, HttpResponseRedirect
from django.urls import reverse
from .NBA_Beautiful_Data.src import analytics_API as Api
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


def plot(request, graph_id):
    """
    The plotting view for the NBA data set.

    :param request: HTML request object
    :return: The html page
    """
    print('\nIN PLOT VIEW')
    print(request.POST)

    # todo, need to user post/redirect/get pattern to avoid refresh causing new entry
    graph = Graph.objects.get(pk=graph_id)
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
        req_graph = Graph(x_key=template_dict['selected_x_key'],
                          y_key=template_dict['selected_y_key'],
                          team=template_dict['selected_team_name'],
                          trend_line=sf.trend_choices[trend_pk],
                          grid=sf.grid_choices[grid_pk],
                          min_seconds=template_dict['selected_min_seconds'],
                          max_seconds=template_dict['selected_max_seconds'])
        prev_id = int(request.POST.get('graph_id'))
        prev_graph = get_object_or_404(Graph, pk=prev_id)
        if not compare_graphs(req_graph, prev_graph):
            # the graphs were different, save the request graph
            print('the graphs were different, save the request graph')
            req_graph.save()
            graph = req_graph
        else:
            print('the graphs were not different, not saving')
            graph = prev_graph

    d = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(d, 'Media')):
        os.mkdir(os.path.join(d, 'Media'))
        os.mkdir(os.path.join(d, 'Media', 'Plots'))
    location = os.path.join(d, 'Media', 'Plots')
    for f in os.listdir(location):
        f_path = os.path.join(location, f)
        if os.path.getmtime(f_path) > 30:
            os.remove(f_path)

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


def compare_graphs(a, b):
    """
    Compares two graph objects.

    :param Graph a: first graph
    :param Graph b: second graph
    :return:
    """
    x_key = (a.x_key == b.x_key)
    # print('%s %s %s' % (x_key, a.x_key, b.x_key))
    y_key = (a.y_key == b.y_key)
    # print('%s %s %s' % (y_key, a.y_key, b.y_key))
    team = (a.team == b.team)
    # print('%s %s %s' % (team, a.team, b.team))
    trend = (a.trend_line == b.trend_line)
    # print('%s %s %s' % (trend, a.trend_line, b.trend_line))
    grid = (a.grid == b.grid)
    # print('%s %s %s' % (grid, a.grid, b.grid))
    max_seconds = (a.max_seconds == b.max_seconds)
    # print('%s %s %s' % (max_seconds, a.max_seconds, b.max_seconds))
    min_seconds = (a.min_seconds == b.min_seconds)
    # print('%s %s %s' % (min_/seconds, a.min_seconds, b.min_seconds))
    return x_key and y_key and team and trend and grid and max_seconds and min_seconds
