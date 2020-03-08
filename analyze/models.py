import logging
import os
import datetime
import random
import string
from collections import OrderedDict
from django.db import models
from .NBA_Beautiful_Data.src import analytics_API as Api
from mysite import settings
from analyze import constants


plot_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(settings.BASE_DIR, 'analyze', 'static', 'analyze', 'data', 'player_box_scores.csv')


def generate_random_alphanumeric(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class Graph(models.Model):
    """
    -NOTE-
    This class is not intended to be used without extending!
    """
    # SQL fields
    graph_id = models.AutoField(primary_key=True)
    x_key = models.CharField(max_length=50)
    y_key = models.CharField(max_length=50)
    trend_line = models.CharField(max_length=50)
    grid = models.CharField(max_length=50)
    min_seconds = models.IntegerField(default=0)
    max_seconds = models.IntegerField(default=6000)
    outlier_count = models.IntegerField(default=5)
    # auto_pseudoid = models.CharField(max_length=16, blank=True, editable=False, unique=True, db_index=True)

    # def save(self, *args, **kwargs):
    #     if not self.auto_pseudoid:
    #         self.auto_pseudoid = self.generate_random_alphanumeric(16)
    #         # using your function as above or anything else
    #     success = False
    #     failures = 0
    #     while not success:
    #         try:
    #             super(Graph, self).save(*args, **kwargs)
    #         except IntegrityError:
    #             failures += 1
    #             if failures > 5:  # or some other arbitrary cutoff point at which things are clearly wrong
    #                 raise
    #             else:
    #                 # looks like a collision, try another random value
    #                 self.auto_pseudoid = self.generate_random_alphanumeric(16)
    #         else:
    #             success = True

    def __str__(self):
        return '%s_%s_min_%s_max_%s' % (str(self.x_key), str(self.y_key), self.min_seconds, self.max_seconds)

    def get_outlier_dict(self):
        return self.create_outlier_template_dict()

    def get_svg_text(self):
        plot_path = self.create_graph(save_path='svg_buffer')
        return plot_path

    def get_search_terms(self):
        """
        :rtype: list
        """
        return NotImplementedError

    def create_graph(self, save_path):
        df = Api.get_existing_data_frame(csv_path, logger=logging.getLogger(__name__))
        search_terms = self.get_search_terms()
        # print('Search terms: %s' % search_terms)
        if self.x_key == 'date':
            # noinspection PyTypeChecker
            plot_path = Api.create_date_plot(y_key=str(self.y_key),
                                             search_terms=search_terms,
                                             df=df,
                                             save_path=save_path,
                                             grid=(str(self.grid) != 'Disable'),
                                             mean_line=(str(
                                                 self.trend_line) != 'Disable'),
                                             num_outliers=self.outlier_count,
                                             min_seconds=self.min_seconds,
                                             max_seconds=self.max_seconds)
        else:
            plot_path = Api.create_scatter_plot_with_trend_line(x_key=str(self.x_key),
                                                                y_key=str(self.y_key),
                                                                df=df,
                                                                save_path=save_path,
                                                                grid=(str(self.grid) != 'Disable'),
                                                                trend_line=(str(
                                                                    self.trend_line) != 'Disable'),
                                                                num_outliers=self.outlier_count,
                                                                teams=search_terms,
                                                                min_seconds=self.min_seconds,
                                                                max_seconds=self.max_seconds)
        return plot_path

    def prepare_outliers(self):
        """
        Gets the svg code for the desired plot.

        :return: outlier data
        :rtype: dict
        """
        df = Api.get_existing_data_frame(csv_path=csv_path, logger=logging.getLogger(__name__))

        search_terms = self.get_search_terms()
        total_df = Api.apply_graph_filters(df=df, search_terms=search_terms, min_seconds=self.min_seconds,
                                           max_seconds=self.max_seconds)
        if Api.convert_team_name(search_terms[0]) in constants.ScatterFilters.teams and self.x_key == 'date':
            total_df = Api.get_team_df(df=total_df)
        outlier_df = total_df.sort_values(by=[self.y_key], ascending=False)
        outlier_df = outlier_df.head(n=self.outlier_count)

        describe_dict = total_df.describe().to_dict()
        describe_dict = describe_dict[str(self.y_key)]
        operations_dict = OrderedDict()
        operations_dict['(Percentiles)'] = ''
        for k, v in sorted(describe_dict.items()):
            operations_dict['%s:' % k] = round(v, 3)
        # print(operations_dict)
        outliers_data = []
        outliers_list = []
        for _, row in outlier_df.sort_values(by=str(self.y_key), ascending=False).iterrows():
            outliers_data.append(self.fix_outlier_dict(row_series=row, df=df))
        if Api.convert_team_name(search_terms[0]) in constants.ScatterFilters.teams and self.x_key == 'date':
            outlier_df = outlier_df.set_index('date')
        outlier_str = outlier_df[[str(self.y_key)]].sort_values(by=str(self.y_key), ascending=False).to_string()
        # print(outlier_str)
        outlier_str = ' '.join(outlier_str.split())
        name = ''
        outlier_format_str = '{0: <6}'
        print(outlier_str.split()[2:])
        if search_terms[0] in constants.ScatterFilters.teams and self.x_key == 'date':
            for index, o in enumerate(outlier_str.split()[2:], start=2):
                print(index, o)
                if len(outliers_list) >= 15:
                    break
                # print(index % 2)
                if index % 2 == 0:
                    converted_date = datetime.datetime.strptime(o, '%y_%m_%d').strftime('%B %d, %Y')
                    name = '%s ' % converted_date
                else:
                    outliers_list.append((outlier_format_str.format(float(o)), name[:-1]))
                    print(outliers_list)
                    name = ''
        else:
            for o in outlier_str.split()[1:]:
                if len(outliers_list) >= 15:
                    break
                try:
                    float(o)
                    outliers_list.append((outlier_format_str.format(float(o)), name[:-1]))
                    print(outliers_list)
                    name = ''
                except ValueError:
                    name += '%s ' % o
        figure_dict = {
            'operations_dict': operations_dict,
            'outliers_list': outliers_list,
            'outliers_data': outliers_data,
        }

        # todo update to properly check if plot is none?
        return figure_dict, total_df

    def create_outlier_template_dict(self):
        template_dict = {}
        fig_data, filtered_df = self.prepare_outliers()

        # filtered_df could be used to save to csv if wanted later
        template_dict['operations_dict'] = fig_data['operations_dict']
        template_dict['outliers_list'] = fig_data['outliers_list']
        template_dict['outliers_data'] = fig_data['outliers_data']
        template_dict['outlier_keys'] = ['game_score', 'minutes_played', 'turnovers',
                                         'ast/to', 'personal_fouls', 'defensive_rebounds', 'offensive_rebounds']

        return template_dict

    def fix_outlier_dict(self, row_series, df):
        """
        Cleans up key names for handling outlier data.

        :param pandas.Series row_series: The row to iterate over
        :param pandas.DataFrame df: The data set to reference
        :return: The more human readable dictionary
        """
        temp_dict = OrderedDict()
        # print(row_series.describe())

        converted_date = datetime.datetime.strptime(row_series['date'], '%y_%m_%d').strftime('%B %d, %Y')
        # print(row_series.name)
        # print(type(row_series.name))
        team = None
        if Api.convert_team_name(row_series.name) in constants.ScatterFilters.teams and self.x_key == 'date':
            print('TEAM OUTLIER')
            # Date played will appear on main view
            temp_dict['name'] = converted_date
            team = row_series.name
        else:
            team = row_series['team']
            temp_dict['name'] = row_series.name
            temp_dict['team'] = Api.convert_team_name(team)
            temp_dict['date'] = converted_date
            temp_dict['ast/to'] = row_series['assist_turnover_ratio']
            temp_dict['minutes_played'] = round(float(row_series['points']), 1)
            temp_dict['game_score'] = round(float(row_series['game_score']), 2)
            temp_dict['true_shooting'] = '%s%%' % round(float(row_series['true_shooting']) * 100, 2)

        temp_dict['opponent'] = row_series['opponent'].replace('_', ' ').title()
        fgp = float(row_series['made_field_goals']) / float(row_series['attempted_field_goals']) if \
            float(row_series['attempted_field_goals']) > 0 else 0
        temp_dict['FGp'] = '%s%% (%s/%s)' % (round((fgp * 100), 1),
                                             int(row_series['made_field_goals']),
                                             int(row_series['attempted_field_goals']))
        three_pt = float(row_series['made_three_point_field_goals']) / float(
            row_series['attempted_three_point_field_goals']) if \
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

        temp_dict['personal_fouls'] = int(row_series['personal_fouls'])
        temp_dict['defensive_rebounds'] = int(row_series['defensive_rebounds'])
        temp_dict['offensive_rebounds'] = int(row_series['offensive_rebounds'])
        temp_dict['points'] = int(row_series['points'])
        temp_dict['rebounds'] = int(row_series['rebounds'])
        temp_dict['assists'] = int(row_series['assists'])
        temp_dict['steals'] = int(row_series['steals'])
        temp_dict['blocks'] = int(row_series['blocks'])
        # todo these will need special care
        temp_dict['outcome'] = row_series['outcome']
        temp_dict['location'] = row_series['location']
        # todo maybe
        temp_dict['team_result'] = Api.get_team_result_on_date(team=Api.convert_team_name(team),
                                                               date=datetime.datetime.strptime(row_series['date'],
                                                                                               '%y_%m_%d'), df=df)

        return temp_dict

    def create_png_location(self, save_dir=os.path.join(plot_dir, 'Media', 'Plots')):
        save_path = os.path.join(save_dir, '%s_vs_%s_min_%s_max_%s.png' % (str(self.x_key),
                                                                           str(self.y_key),
                                                                           self.min_seconds,
                                                                           self.max_seconds))
        self.create_graph(save_path=save_path)
        # there should probably be a check to make sure the graph update worked but for now just assume it did
        return save_path


class TeamGraph(Graph):
    teams = models.CharField(max_length=200)

    def __str__(self):
        return '%s_%s_%s_%s' % (self.graph_id, str(self.x_key), str(self.y_key), self.teams)

    def get_search_terms(self):
        return str(self.teams).split(",")


class PlayerGraph(Graph):
    players = models.CharField(max_length=200)

    def __str__(self):
        return '%s_%s_%s_%s' % (self.graph_id, str(self.x_key), str(self.y_key), self.players)

    def get_search_terms(self):
        return str(self.players).split(",")
