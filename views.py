from django.shortcuts import render
from matplotlib import pyplot as plt
import io
from .NBA_Beautiful_Data.analytics import analytics_API as Api
import logging
from .models import ScatterKeysYAxis, ScatterKeysXAxis, BasketballTeamName

# Create your views here.


def index(request):
    # can provide optional 3rd arg of dictionary to pass to template
    return render(request, 'analyze/index.html', {})


def plot(request):
    """
    The plotting view for the NBA data set.

    :param request: HTML request object
    :return: The html page
    """
    # defaults
    x_key = 'minutes_played'
    y_key = 'game_score'
    team_name = 'Select a Team'
    grid = 'True'
    min_seconds = 0
    max_seconds = 100 * 60
    if request.method == "POST":
        # try to get the new x_key, default otherwise
        x_key = request.POST.get('x_key_name', 'minutes_played')
        y_key = request.POST.get('y_key_name', 'game_score')
        grid = request.POST.get('grid_enable', 'True')
        team_name = request.POST.get('team_name', 'Select a Team')
        min_seconds = request.POST.get('min_seconds', 0)
        max_seconds = request.POST.get('max_seconds', 100 * 60)

    # set the boolean value based on string value
    grid = (grid == 'True')
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

    # dict that is passed to the html template file
    svg_dict = {
        'svg': get_fig(x_key=x_key, y_key=y_key, grid=grid, teams=teams, min_seconds=min_seconds,
                       max_seconds=max_seconds),
        'selected_x_key': x_key,
        'selected_y_key': y_key,
        'selected_team_name': team_name,
        'grid_enabled': grid,
        'min_seconds': min_seconds,
        'max_seconds': max_seconds,
        'y_keys': ScatterKeysYAxis.objects.all(),
        'x_keys': ScatterKeysXAxis.objects.all(),
        'team_names': BasketballTeamName.objects.all(),
    }  # set the plot data

    # clean up plt so it can be re-used
    plt.cla()

    return render(request, 'analyze/plot.html', svg_dict)


def get_fig(x_key, y_key, grid, teams, min_seconds, max_seconds):
    """
    Gets the svg code for the desired plot.

    :param str x_key: Key for the x axis
    :param str y_key: Key for the y axis
    :param bool grid: Determines if the plot should contain a grid
    :param list teams: Teams to filter on
    :param int min_seconds: Minimum seconds played to filter on
    :param int max_seconds: Maximum seconds played to filter on
    :return: svg figure code
    """
    my_csv = r'C:\Users\User\Desktop\Programs\testproj\mysite\analyze\NBA_Beautiful_Data\player_box_scores.csv'
    df = Api.get_existing_data_frame(my_csv, logger=logging.getLogger(__name__))
    Api.create_scatter_plot_with_trend_line(x_key=x_key,
                                            y_key=y_key,
                                            df=df,
                                            grid=grid,
                                            outliers=5,
                                            teams=teams,
                                            min_seconds=min_seconds,
                                            max_seconds=max_seconds)

    fig_file = io.StringIO()
    plt.savefig(fig_file, format='svg', bbox_inches='tight')

    # grab the svg data to embed directly into the html file
    fig_data_svg = '<svg' + fig_file.getvalue().split('<svg')[1]
    fig_file.close()
    return fig_data_svg
