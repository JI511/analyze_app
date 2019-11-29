from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
import random
import numpy as np
from matplotlib import pyplot as plt
import io
from .NBA_Beautiful_Data.analytics import analytics_API as Api
import pandas as pd
import logging

# Create your views here.


def index(request):
    # can provide optional 3rd arg of dictionary to pass to template
    return render(request, 'analyze/index.html', {})


def plot(request):
    # setPlt()  # create the plot
    svg_dict = {'svg': get_fig()}  # set the plot data
    plt.cla()  # clean up plt so it can be re-used
    return render(request, 'analyze/plot.html', svg_dict)


def get_fig():
    my_csv = r'C:\Users\User\Desktop\Programs\testproj\mysite\analyze\NBA_Beautiful_Data\player_box_scores.csv'
    # my_csv = r'C:\Users\ingwe\Desktop\Programs\django_practice\mysite\analyze\NBA_Beautiful_Data\player_box_scores.csv'
    df = Api.get_existing_data_frame(my_csv, logger=logging.getLogger(__name__))

    x_key = 'minutes_played'
    y_key = 'game_score'
    Api.create_scatter_plot_with_trend_line(x_key=x_key, y_key=y_key, df=df, outliers=5)

    fig_file = io.StringIO()
    plt.savefig(fig_file, format='svg', bbox_inches='tight')
    fig_data_svg = '<svg' + fig_file.getvalue().split('<svg')[1]
    fig_file.close()
    return fig_data_svg
