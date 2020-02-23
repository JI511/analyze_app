# ----------------------------------------------------------------------------------------------------------------------
# Analytics API
# ----------------------------------------------------------------------------------------------------------------------

# imports
import datetime
import os
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as plt_dates
from analyze import constants


plt.switch_backend('agg')


def get_existing_data_frame(csv_path, logger):
    """
    Determines if a data frame already exists, and returns the data frame if true. Returns None if does not exist.
    :param str csv_path: Path of the csv file.
    :param logger: Instance of logger object.
    :return: Data frame if exists, None otherwise
    :rtype: pd.DataFrame
    """
    df = None
    if os.path.exists(csv_path):
        logger.info("Existing data frame found.")
        df = pd.read_csv(csv_path, index_col=0)
    return df


def convert_team_name(team):
    """
    Converts team string into proper casing format

    :param str team: Team enum name
    :return: Converted string
    """
    return team.title().replace('_', ' ')


def get_team_date_df(df, team, date):
    """
    Attempts to make a pandas data frame of all player box scores on a certain day.

    :param pandas.DataFrame df: The data frame to search.
    :param str team: The team to search for.
    :param datetime.datetime date: The date to search on.
    :return: Team data frame if found
    """
    team_df = None
    if isinstance(date, datetime.datetime):
        converted_date = date.strftime('%y_%m_%d')
        team_df = df[(df['date'] == converted_date) & (df['team'] == team)]
    return team_df


def filter_df_on_team_names(df, teams):
    """
    Returns a new data frame object only containing rows where the team matches any of the provided team names.

    :param pandas.DataFrame df: The data frame to search.
    :param list teams: The teams to filter on.
    :return: Team filtered data frame, or the original if none of the specified teams are found.
    """
    teams = [entry.upper().replace(' ', '_') for entry in teams]
    team_df = df[df['team'].isin(teams)]
    return team_df

def filter_df_on_player_names(df, players):
    """
    todo

    :param pandas.DataFrame df: The data frame to search.
    :param list players: The player names to filter on.
    :return: Player name filtered data frame.
    """
    player_df = df
    if np.any(df.index.isin(players)):
        player_df = df[df.index.isin(players)]
    return player_df

def get_most_recent_update_date(df, date_col='date'):
    """
    Gets the most recent date from the pandas.DataFrame provided.

    :param pandas.DataFrame df: The pandas.DataFrame object
    :param str date_col: The column to reference in the DataFrame object
    :return: The date found
    :rtype: datetime.datetime
    """
    temp_series = pd.to_datetime(df[date_col], format='%y_%m_%d')
    temp_date = str(temp_series.max()).split()[0].split('-')
    return datetime.datetime(year=int(temp_date[0]), month=int(temp_date[1]), day=int(temp_date[2]))


def get_team_result_on_date(team, date, df):
    """
    Calculates the team scores on a particular date.

    :param str team: Team to search for
    :param datetime.datetime date: The date to search on
    :param pandas.DataFrame df: The data set to search in
    :return: The score as a string, ex: 97-88. The desired team's score will always be first.
    """
    converted_team = team.replace(' ', '_').upper()
    converted_date = date.strftime('%y_%m_%d')
    team_df = df[(df['team'] == converted_team) & (df['date'] == converted_date) & (df['points'] > 0)]
    opp_team = team_df['opponent'].values[0]
    opp_df = df[(df['team'] == opp_team) & (df['date'] == converted_date) & (df['points'] > 0)]
    res = '%s-%s' % (int(np.sum(team_df['points'])), int(np.sum(opp_df['points'])))
    return res


def apply_graph_filters(df, **kwargs):

    search_terms = kwargs.get('teams', None)
    min_seconds = kwargs.get('min_seconds', 0)
    max_seconds = kwargs.get('max_seconds', 6000)

    # filters
    # todo
    if search_terms is not None and isinstance(search_terms, list):
        if search_terms[0] in constants.ScatterFilters.teams:
            df = filter_df_on_team_names(df, search_terms)
        else:
            df = filter_df_on_player_names(df, search_terms)
    if min_seconds is not None and isinstance(min_seconds, int):
        if min_seconds >= 60:
            df = df[df['seconds_played'] >= min_seconds]
        else:
            df = df[df['minutes_played'] >= min_seconds]
    if max_seconds is not None and isinstance(max_seconds, int):
        if max_seconds >= 60:
            df = df[df['seconds_played'] <= max_seconds]
        else:
            df = df[df['minutes_played'] <= max_seconds]
    return df


def handle_plot_output(save_path):
    """
    todo
    :param save_path:
    :return:
    """
    # handle output
    plot_path = None
    if save_path is not None:
        if save_path == 'svg_buffer':
            fig_file = io.StringIO()
            plt.savefig(fig_file, format='svg', bbox_inches='tight')
            fig_data_svg = '<svg' + fig_file.getvalue().split('<svg')[1]
            fig_file.close()
            plot_path = fig_data_svg
        else:
            # save at the path given
            plt.savefig(save_path)
            plot_path = save_path
        plt.clf()
        plt.cla()
        plt.close('all')
    return plot_path


def create_scatter_plot_with_trend_line(x_key, y_key, df, **kwargs):
    """
    Creates a scatter plot for two different series of a pandas data frame.

    :param str x_key: The column name in the data frame to use for the x axis.
    :param str y_key: The column name in the data frame to use for the x axis.
    :param pandas.DataFrame df: The data frame object.

    Supported kwargs:
        bool grid: Indicates if a grid should be added to the plot.
        int num_outliers: The number of outliers to label on the plot.
        list teams: The team names to filter on if wanted.
        int min_seconds: The minimum number of seconds played to filter on if needed.
        int max_seconds: The maximum number of seconds played to filter on if needed.
        str save_path: The path to save the png file created.
        bool show_plot: Indicates if the png should be shown during execution.
        bool trend_line: Indicates if a trend line should be shown.

    :return: The save path of the created png, the outlier DataFrame, the filtered DataFrame.
    :rtype: tuple
    """
    search_terms = kwargs.get('teams', None)
    save_path = kwargs.get('save_path', None)
    show_plot = kwargs.get('show_plot', False)
    min_seconds = kwargs.get('min_seconds', 0)
    max_seconds = kwargs.get('max_seconds', 6000)
    num_outliers = kwargs.get('num_outliers', 5)
    grid = kwargs.get('grid', True)
    trend_line = kwargs.get('trend_line', True)

    # filters
    df = apply_graph_filters(df=df, teams=search_terms, min_seconds=min_seconds, max_seconds=max_seconds)

    temp_df = df[[x_key, y_key]]
    thresh = get_outlier_threshold(y_key=y_key, temp_df=temp_df, num_outliers=num_outliers)

    main_df = temp_df[temp_df[y_key] < thresh]
    title = '%s vs %s (%s samples)' % (x_key.title().replace('_', ' '),
                                       y_key.title().replace('_', ' '),
                                       temp_df[y_key].shape[0])

    outlier_df = temp_df[temp_df[y_key] >= thresh]
    # plot main df and outliers
    fig, ax = plt.subplots(figsize=(10, 6))
    main_df.plot(kind='scatter', x=x_key, y=y_key, grid=grid, ax=ax)
    outlier_df.plot(kind='scatter', x=x_key, y=y_key, grid=grid, ax=ax)

    ax.set_xlabel(x_key.title().replace('_', ' '))
    ax.set_ylabel(y_key.title().replace('_', ' '))

    # add point labels
    for k, v in outlier_df.iterrows():
        temp_split = k.split(' ')
        name = '%s.%s.' % (temp_split[0][:1], temp_split[1][:3])
        ax.annotate(name, v, xytext=(5, -5), textcoords='offset points')

    # create trend line
    if trend_line:
        x = df[x_key]
        y = df[y_key]
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), "r--", label='Trend')
        plt.legend(loc='lower right')

    # makes things fit on graph window
    plt.title(title)
    plt.tight_layout()

    return handle_plot_output(save_path=save_path)


def get_outlier_threshold(y_key, temp_df, num_outliers):
    series_size = temp_df[y_key].shape[0]
    if series_size > num_outliers:
        thresh = sorted(temp_df[y_key].to_list())[-num_outliers]
    else:
        thresh = 0
    return thresh


def get_scatter_outliers(x_key, y_key, df, **kwargs):

    teams = kwargs.get('teams', None)
    min_seconds = kwargs.get('min_seconds', 0)
    max_seconds = kwargs.get('max_seconds', 6000)
    num_outliers = kwargs.get('num_outliers', 5)

    if num_outliers > 15:
        num_outliers = 15

    df = apply_graph_filters(df=df, teams=teams, min_seconds=min_seconds, max_seconds=max_seconds)
    thresh = get_outlier_threshold(y_key=y_key, temp_df=df[[x_key, y_key]], num_outliers=num_outliers)
    outlier_df_full = df[df[y_key] >= thresh]

    return outlier_df_full


def create_date_plot(y_key, player, df, **kwargs):
    """
    Creates a plot of player data based on a given key.

    :param y_key: The stat to filter on
    :param str player: The name of the player to search for
    :param pandas.DataFrame df: The pandas.DataFrame object to search in

    Supported kwargs:
        save_path: The path to save the plot to or the type of plot to save
        show_plot: Determines if the plot should be shown to the user
        min_seconds: The minimum seconds to filter on
        max_seconds: The maximum seconds to filter on
        num_outliers: The number of outlier data points to collect
        grid: Determines if both x and y axis grids should be used, or just one or the other
        mean_line: Determines if a mean line should be shown of all collected data points

    :return: The path of the created plot, outlier pandas.DataFrame object, full pandas.DataFrame object.
    :rtype: tuple
    """
    save_path = kwargs.get('save_path', None)
    show_plot = kwargs.get('show_plot', False)
    min_seconds = kwargs.get('min_seconds', 0)
    max_seconds = kwargs.get('max_seconds', 6000)
    num_outliers = kwargs.get('num_outliers', 5)  # todo
    grid = kwargs.get('grid', 'both')
    mean_line = kwargs.get('mean_line', True)

    # filters
    perform_plot = True
    if player is not None and isinstance(player, str):
        if np.any(df.index.isin([player])):
            df = df[df.index.isin([player])]
        else:
            # we don't want to try if the player name is invalid
            perform_plot = False
            plot_path = 'Invalid player name of %s' % player
    if isinstance(min_seconds, int) and isinstance(max_seconds, int):
        if max_seconds > min_seconds:
            if min_seconds >= 60:
                df = df[df['seconds_played'] >= min_seconds]
            else:
                df = df[df['minutes_played'] >= min_seconds]
            if max_seconds >= 60:
                df = df[df['seconds_played'] <= max_seconds]
            else:
                df = df[df['minutes_played'] <= max_seconds]
        else:
            plot_path = 'Max seconds < Min seconds'
            perform_plot = False
    else:
        plot_path = 'Max/Min seconds incorrect type %s %s' % (type(min_seconds), type(max_seconds))
        perform_plot = False

    if perform_plot and df.shape[0] > 0:
        df['datetime'] = pd.to_datetime(df['date'], format='%y_%m_%d')
        x_key = 'datetime'
        temp_df = df[[x_key, y_key]]
        series_size = temp_df[y_key].shape[0]
        title = '%s: %s (%s samples)' % (player,
                                         y_key.title().replace('_', ' '),
                                         series_size)
        data_mean = np.mean(temp_df[y_key])
        fig, ax = plt.subplots(figsize=(10, 6))
        temp_df.plot(kind='line', x=x_key, y=y_key, style='.', ms=10, ax=ax)
        if mean_line:
            plt.axhline(y=data_mean, label='Mean: %s' % np.round(data_mean, 1), color='red')
            plt.legend(loc='best')
        ax.set_xlabel('Date (month-day)')
        ax.set_ylabel(y_key.title().replace('_', ' '))
        ax.set_xlim([ax.get_xlim()[0] - 2, ax.get_xlim()[1] + 2])

        # calc x tick dates
        start, end = ax.get_xlim()[0], ax.get_xlim()[1]
        if (end - start) > 0:
            ticks_needed = (end - start) / 4
            x_ticks = [end]
            for i in range(np.cast['int'](ticks_needed)):
                temp_tick = start + (i * 4)
                x_ticks.append(temp_tick)
            ax.set_xticks(x_ticks)
        date_format = plt_dates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(date_format)

        # calc y tick dates
        top = ax.get_ylim()[1]
        if top >= 30:
            y_ticks = [0]
            temp_tick = 5
            while temp_tick < top:
                y_ticks.append(temp_tick)
                temp_tick += 5
            ax.set_yticks(y_ticks)

        if grid != 'none':
            if grid == 'x':
                ax.grid(axis='x')
            elif grid == 'y':
                ax.grid(axis='y')
            else:
                ax.grid()
        plt.title(title)
        plt.tight_layout()

    plot_path = handle_plot_output(save_path=save_path)
    return plot_path


def create_bar_plot(df, bar_items, save_path=None, show_plot=False, team=None, date=None):
    """
    Creates a stacked bar graph with any number of column names for a team.

    :param pandas.DataFrame df: Data frame to use.
    :param list bar_items: Column names within the data frame.
    :param str save_path: The path to save the png file created.
    :param bool show_plot: Indicates if the png should be shown during execution.
    :param str team: Optional team name to add to plot title.
    :param datetime.datetime date: Optional date to add to plot title.
    :return: Save path if save successful.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    margin_bottom = np.zeros(df.shape[0])
    colors = ['#17408B', '#C9082A', '#552084', '#FDBA21']
    title = ''
    for index, item in enumerate(bar_items):
        values = df[item].to_list()
        df.plot.bar(y=item, ax=ax, stacked=True, bottom=margin_bottom, color=colors[index], rot=45, label=item)
        margin_bottom += values
        title += '%s ' % item.title()

    if team is not None:
        if isinstance(team, str):
            title = '%s %s' % (convert_team_name(team), title)

    if date is not None:
        if isinstance(date, datetime.datetime):
            title = '%s %s' % (title, date.strftime('%y_%m_%d'))

    ax.set_title(title)
    plt.tight_layout()

    # handle output
    plot_path = None
    if save_path is not None:
        if os.path.isdir(save_path):
            if not os.path.exists(os.path.join(save_path, 'plots')):
                os.mkdir(os.path.join(save_path, 'plots'))
            if date is None:
                ymd = datetime.datetime.now().strftime("%y%m%d")
                plot_path = os.path.join(save_path, 'plots', '%s_%s' % (title.replace(' ', '_'), ymd))
            else:
                plot_path = os.path.join(save_path, 'plots', title.replace(' ', '_'))
            plt.savefig(plot_path)
    if show_plot:
        plt.show()
    return plot_path


# ----------------------------------------------------------------------------------------------------------------------
# End
# ----------------------------------------------------------------------------------------------------------------------
