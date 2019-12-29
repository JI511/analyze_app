from django.shortcuts import render
from django.http import HttpResponse, Http404
from .NBA_Beautiful_Data.analytics import analytics_API as Api
import logging
from .models import ScatterKeysYAxis, ScatterKeysXAxis, BasketballTeamName
import numpy as np
import shutil
import os
from collections import OrderedDict
import datetime


def index(request):
    # can provide optional 3rd arg of dictionary to pass to template
    return render(request, 'analyze/index.html', {})


def plot(request):
    """
    The plotting view for the NBA data set.

    :param request: HTML request object
    :return: The html page
    """
    save_path = os.path.join(os.getcwd(), 'analyze', 'static', 'analyze', 'images', 'temp_plot')
    if os.path.exists(save_path):
        shutil.rmtree(save_path)

    # defaults
    x_key = 'minutes_played'
    y_key = 'game_score'
    team_name = 'Select a Team'
    grid = 'True'
    trend = 'True'
    min_seconds = 0
    max_seconds = 100 * 60
    if request.method == "POST":
        # try to get the new x_key, default otherwise
        x_key = request.POST.get('x_key_name', 'minutes_played')
        y_key = request.POST.get('y_key_name', 'game_score')
        grid = request.POST.get('grid_enable', 'True')
        trend = request.POST.get('trend_enable', 'True')
        team_name = request.POST.get('team_name', 'Select a Team')
        min_seconds = request.POST.get('min_seconds', 0)
        max_seconds = request.POST.get('max_seconds', 100 * 60)

    # set the boolean value based on string value
    grid = (grid == 'True')
    trend = (trend == 'True')
    teams = [team_name] if team_name != 'Select a Team' else None

    # check each separately so the other will persist if one is not a valid int
    try:
        min_seconds = int(min_seconds)
    except ValueError:
        min_seconds = 0
    try:
        max_seconds = int(max_seconds)
    except ValueError:
        max_seconds = 100 * 60
    plot_png, operations_dict, outliers, outliers_data = get_fig(x_key=x_key, y_key=y_key, grid=grid, teams=teams,
                                                                 trend=trend,
                                                                 min_seconds=min_seconds, max_seconds=max_seconds)
    # dict that is passed to the html template file
    svg_dict = {
        'fig': plot_png,
        'selected_x_key': x_key,
        'selected_y_key': y_key,
        'selected_team_name': team_name,
        'grid_enabled': grid,
        'trend_enabled': trend,
        'min_seconds': min_seconds,
        'max_seconds': max_seconds,
        'op_dict': operations_dict,
        'outliers': outliers,
        'outliers_data': outliers_data,
        'y_keys': ScatterKeysYAxis.objects.all(),
        'x_keys': ScatterKeysXAxis.objects.all(),
        'team_names': BasketballTeamName.objects.all(),
    }  # set the plot data

    return render(request, 'analyze/plot.html', svg_dict)


def get_fig(x_key, y_key, grid, teams, trend, min_seconds, max_seconds):
    """
    Gets the svg code for the desired plot.

    :param str x_key: Key for the x axis
    :param str y_key: Key for the y axis
    :param bool grid: Determines if the plot should contain a grid
    :param list teams: Teams to filter on
    :param bool trend: Determines if the trend line should be shown
    :param int min_seconds: Minimum seconds played to filter on
    :param int max_seconds: Maximum seconds played to filter on
    :return: svg figure code
    """
    save_path = os.path.join(os.getcwd(), 'analyze', 'static', 'analyze', 'images', 'temp_plot')
    my_csv = r'C:\Users\User\Desktop\Programs\testproj\mysite\analyze\NBA_Beautiful_Data\player_box_scores.csv'
    df = Api.get_existing_data_frame(my_csv, logger=logging.getLogger(__name__))
    temp_csv_path = os.path.join(save_path, 'temp_plot_data.csv')
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    outlier_count = 5

    temp_name = 'temp_plot.png'
    plot_path, outlier_df, total_df = Api.create_scatter_plot_with_trend_line(x_key=x_key,
                                                                              y_key=y_key,
                                                                              df=df,
                                                                              save_path=os.path.join(save_path,
                                                                                                     temp_name),
                                                                              grid=grid,
                                                                              trend_line=trend,
                                                                              num_outliers=outlier_count,
                                                                              teams=teams,
                                                                              min_seconds=min_seconds,
                                                                              max_seconds=max_seconds)
    describe_dict = total_df.describe().to_dict()
    describe_dict = describe_dict[y_key]
    operations_dict = OrderedDict()
    operations_dict['(Percentiles)'] = ''
    for k, v in sorted(describe_dict.items()):
        operations_dict['%s:' % k] = round(v, 3)
    outliers_data = []
    outliers_list = []
    for _, row in outlier_df.sort_values(by=y_key, ascending=False).iterrows():
        outliers_data.append(fix_outlier_dict(row_series=row))
    outlier_str = outlier_df[[y_key]].sort_values(by=y_key, ascending=False).to_string()
    outlier_str = ' '.join(outlier_str.split())
    name = ''
    outlier_format_str = '{0: <6}'
    for o in outlier_str.split()[1:]:
        if len(outliers_list) >= 15:
            break
        try:
            float(o)
            outliers_list.append((outlier_format_str.format(float(o)), name[:-1]))
            name = ''
        except ValueError:
            name += '%s ' % o
    total_df.to_csv(path_or_buf=temp_csv_path)

    # todo update to properly check if plot is none?
    return os.path.join('analyze', 'images', 'temp_plot', temp_name), operations_dict, outliers_list, outliers_data


def fix_outlier_dict(row_series):
    """
    Cleans up key names for handling outlier data.

    :param row_series: The pandas.Series object
    :return: The more human readable dictionary
    """
    temp_dict = OrderedDict()
    temp_dict['name'] = row_series.name
    temp_dict['team'] = row_series['team'].replace('_', ' ').title()
    temp_dict['opponent'] = row_series['opponent'].replace('_', ' ').title()
    date = convert_date(row_series['date'])
    temp_dict['date'] = date.strftime('%B %d, %Y')
    temp_dict['FG%'] = '%s%% (%s/%s)' % (round((float(row_series['made_field_goals']) /
                                                float(row_series['attempted_field_goals']) * 100), 1),
                                         int(row_series['made_field_goals']),
                                         int(row_series['attempted_field_goals']))
    temp_dict['3pt FG%'] = '%s%% (%s/%s)' % (round((float(row_series['made_three_point_field_goals']) /
                                                    float(row_series['attempted_three_point_field_goals']) * 100), 1),
                                             int(row_series['made_three_point_field_goals']),
                                             int(row_series['attempted_three_point_field_goals']))
    temp_dict['FT%'] = '%s%% (%s/%s)' % (round((float(row_series['made_free_throws']) /
                                                float(row_series['attempted_free_throws']) * 100), 1),
                                         int(row_series['made_free_throws']),
                                         int(row_series['attempted_free_throws']))
    temp_dict['points'] = int(row_series['points'])
    temp_dict['rebounds'] = '%s (%s off, %s def)' % (int(row_series['rebounds']),
                                                     int(row_series['offensive_rebounds']),
                                                     int(row_series['defensive_rebounds']))
    temp_dict['assists'] = int(row_series['assists'])
    temp_dict['steals'] = int(row_series['steals'])
    temp_dict['blocks'] = int(row_series['blocks'])
    temp_dict['turnovers'] = int(row_series['turnovers'])
    temp_dict['ast/to'] = row_series['assist_turnover_ratio']
    temp_dict['true shooting'] = '%s%%' % round(float(row_series['true_shooting']) * 100, 2)

    # keep track of already modified keys
    pre_appended = ['name', 'team', 'date', 'opponent', 'made_field_goals', 'attempted_field_goals',
                    'made_three_point_field_goals', 'attempted_three_point_field_goals', 'made_free_throws',
                    'attempted_free_throws', 'rebounds', 'offensive_rebounds', 'defensive_rebounds', 'points',
                    'assists', 'steals', 'blocks', 'turnovers', 'assist_turnover_ratio', 'true_shooting']
    for key in sorted(row_series.to_dict().keys()):
        if key not in pre_appended:
            data = row_series[key]
            key = key.replace('_', ' ')
            temp_dict[key] = data

    return temp_dict


def convert_date(date_string):
    """
    Gets a datetime object from a date string.

    :param date_string: The date string
    :return: datetime.datetime object
    """
    return datetime.datetime.strptime(date_string, '%y_%m_%d')


def get_team_result():
    pass
