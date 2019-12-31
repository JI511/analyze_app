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


# VIEWS
def index(request):
    # can provide optional 3rd arg of dictionary to pass to template
    return render(request, 'analyze/index.html', {})


def plot(request):
    """
    The plotting view for the NBA data set.

    :param request: HTML request object
    :return: The html page
    """

    fig_dict = handle_graph_update(request=request)

    # dict that is passed to the html template file
    svg_dict = {
        'fig_dict': fig_dict,
        # 'selected_x_key': fig_dict['x_key'],
        # 'selected_y_key': figy_key,
        # 'selected_team_name': team_name,
        # 'grid_enabled': grid,
        # 'trend_enabled': trend,
        # 'min_seconds': min_seconds,
        # 'max_seconds': max_seconds,
        # 'op_dict': fig_data['operations_dict'],
        # 'outliers': fig_data['outliers_list'],
        # 'outliers_data': fig_data['outliers_data'],
        # 'outlier_keys': outlier_keys,
        'y_keys': ScatterKeysYAxis.objects.all(),
        'x_keys': ScatterKeysXAxis.objects.all(),
        'team_names': BasketballTeamName.objects.all(),
    }  # set the plot data

    return render(request, 'analyze/plot.html', svg_dict)


# HELPERS
def handle_graph_update(request):
    # defaults
    template_dict = {
        'selected_x_key': request.POST.get('x_key_name', 'minutes_played'),
        'selected_y_key': request.POST.get('y_key_name', 'game_score'),
        'selected_team_name': request.POST.get('team_name', 'Select a Team'),
        'grid_enable': request.POST.get('grid_enable', 'True'),
        'trend_enable': request.POST.get('trend_enable', 'True'),
        'min_seconds': request.POST.get('min_seconds', 0),
        'max_seconds': request.POST.get('max_seconds', 100 * 60),
    }
    # if request.method == "POST":
    #     # try to get the new x_key, default otherwise
    #     x_key = request.POST.get('x_key_name', 'minutes_played')
    #     y_key = request.POST.get('y_key_name', 'game_score')
    #     grid = request.POST.get('grid_enable', 'True')
    #     trend = request.POST.get('trend_enable', 'True')
    #     team_name = request.POST.get('team_name', 'Select a Team')
    #     min_seconds = request.POST.get('min_seconds', 0)
    #     max_seconds = request.POST.get('max_seconds', 100 * 60)

    # set the boolean value based on string value
    template_dict['grid_enable'] = (template_dict['grid_enable'] == 'True')
    template_dict['trend_enable'] = (template_dict['trend_enable'] == 'True')
    template_dict['teams'] = [template_dict['selected_team_name']] if template_dict['selected_team_name'] != \
        'Select a Team' else None

    # check each separately so the other will persist if one is not a valid int
    try:
        template_dict['min_seconds'] = int(template_dict['min_seconds'])
    except ValueError:
        template_dict['min_seconds'] = 0
    try:
        template_dict['max_seconds'] = int(template_dict['max_seconds'])
    except ValueError:
        template_dict['max_seconds'] = 100 * 60

    fig_data, filtered_df = get_fig(x_key=template_dict['selected_x_key'],
                                    y_key=template_dict['selected_y_key'],
                                    grid=template_dict['grid_enable'],
                                    teams=template_dict['teams'],
                                    trend=template_dict['trend_enable'],
                                    min_seconds=template_dict['min_seconds'],
                                    max_seconds=template_dict['max_seconds'])
    template_dict['svg_data'] = fig_data['svg_data']
    template_dict['operations_dict'] = fig_data['operations_dict']
    template_dict['outliers_list'] = fig_data['outliers_list']
    template_dict['outliers_data'] = fig_data['outliers_data']
    template_dict['outlier_keys'] = ['game_score', 'minutes_played', 'turnovers',
                                     'ast/to', 'personal_fouls', 'defensive_rebounds', 'offensive_rebounds']

    for key, val in template_dict.items():
        if key != 'svg_data':
            print('key', key)
            print('\tvalue', val)
    return template_dict


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
    csv_path = os.path.join(os.getcwd(), 'analyze', 'static', 'analyze', 'data', 'player_box_scores.csv')
    df = Api.get_existing_data_frame(csv_path=csv_path, logger=logging.getLogger(__name__))

    outlier_count = 5
    # plot_path will be the svg data as a string
    # total_df will be the filtered df
    plot_path, outlier_df, total_df = Api.create_scatter_plot_with_trend_line(x_key=x_key,
                                                                              y_key=y_key,
                                                                              df=df,
                                                                              save_path='svg_buffer',
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
        outliers_data.append(fix_outlier_dict(row_series=row, df=df))
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
    figure_dict = {
        'svg_data': plot_path,
        'operations_dict': operations_dict,
        'outliers_list': outliers_list,
        'outliers_data': outliers_data,
    }

    # todo update to properly check if plot is none?
    return figure_dict, total_df


def fix_outlier_dict(row_series, df):
    """
    Cleans up key names for handling outlier data.

    :param pandas.Series row_series: The row to iterate over
    :param pandas.DataFrame df: The data set to reference
    :return: The more human readable dictionary
    """
    temp_dict = OrderedDict()

    temp_dict['name'] = row_series.name
    temp_dict['team'] = row_series['team'].replace('_', ' ').title()
    temp_dict['opponent'] = row_series['opponent'].replace('_', ' ').title()
    date = convert_date(row_series['date'])
    temp_dict['date'] = date.strftime('%B %d, %Y')
    fgp = float(row_series['made_field_goals']) / float(row_series['attempted_field_goals']) if \
        float(row_series['attempted_field_goals']) > 0 else 0
    temp_dict['FGp'] = '%s%% (%s/%s)' % (round((fgp * 100), 1),
                                         int(row_series['made_field_goals']),
                                         int(row_series['attempted_field_goals']))
    three_pt = float(row_series['made_three_point_field_goals']) / \
        float(row_series['attempted_three_point_field_goals']) if \
        float(row_series['attempted_three_point_field_goals']) > 0 else 0
    temp_dict['3ptFGp'] = '%s%% (%s/%s)' % (round((three_pt * 100), 1),
                                            int(row_series['made_three_point_field_goals']),
                                            int(row_series['attempted_three_point_field_goals']))
    ftp = float(row_series['made_free_throws']) / float(row_series['attempted_free_throws']) if \
        float(row_series['attempted_free_throws']) > 0 else 0
    temp_dict['FTp'] = '%s%% (%s/%s)' % (round((ftp * 100), 1),
                                         int(row_series['made_free_throws']),
                                         int(row_series['attempted_free_throws']))

    temp_dict['turnovers'] = int(row_series['turnovers'])
    temp_dict['ast/to'] = row_series['assist_turnover_ratio']
    temp_dict['minutes_played'] = round(float(row_series['points']), 1)
    temp_dict['personal_fouls'] = int(row_series['personal_fouls'])
    temp_dict['defensive_rebounds'] = int(row_series['defensive_rebounds'])
    temp_dict['offensive_rebounds'] = int(row_series['offensive_rebounds'])
    temp_dict['game_score'] = round(float(row_series['game_score']), 2)

    temp_dict['points'] = int(row_series['points'])
    temp_dict['rebounds'] = int(row_series['rebounds'])
    temp_dict['assists'] = int(row_series['assists'])
    temp_dict['steals'] = int(row_series['steals'])
    temp_dict['blocks'] = int(row_series['blocks'])
    temp_dict['outcome'] = row_series['outcome']
    temp_dict['location'] = row_series['location']
    temp_dict['true_shooting'] = '%s%%' % round(float(row_series['true_shooting']) * 100, 2)
    temp_dict['team_result'] = Api.get_team_result_on_date(team=temp_dict['team'], date=date, df=df)

    return temp_dict


def convert_date(date_string):
    """
    Gets a datetime object from a date string.

    :param date_string: The date string
    :return: datetime.datetime object
    """
    return datetime.datetime.strptime(date_string, '%y_%m_%d')
