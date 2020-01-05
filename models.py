import logging
import os
import datetime
from collections import OrderedDict
from django.db import models
from .NBA_Beautiful_Data.analytics import analytics_API as Api
from mysite import settings


class Graph(models.Model):
    # SQL fields
    graph_id = models.AutoField(primary_key=True)
    x_key = models.CharField(max_length=50)
    y_key = models.CharField(max_length=50)
    team = models.CharField(max_length=50)
    trend_line = models.CharField(max_length=50)
    grid = models.CharField(max_length=50)
    min_seconds = models.IntegerField(default=0)
    max_seconds = models.IntegerField(default=6000)
    outlier_count = models.IntegerField(default=5)

    # other object vars
    plot_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(settings.BASE_DIR, 'analyze', 'static', 'analyze', 'data', 'player_box_scores.csv')
    png_save_dir = save_path = os.path.join(plot_dir, 'Media', 'Plots')

    def __str__(self):
        return '%s_%s_%s_min_%s_max_%s' % (str(self.x_key), str(self.y_key), self.team, self.min_seconds,
                                           self.max_seconds)

    def get_svg_text(self):
        plot_path, _, _ = self.__update_graph_and_save(save_path='svg_buffer')
        return plot_path

    def create_png_location(self):
        save_path = os.path.join(self.png_save_dir, '%s_vs_%s_min_%s_max_%s.png' % (str(self.x_key),
                                                                                    str(self.y_key),
                                                                                    self.min_seconds,
                                                                                    self.max_seconds))
        print(save_path)
        self.__update_graph_and_save(save_path=save_path)
        # there should probably be a check to make sure the graph update worked but for now just assume it did
        return save_path

    def get_outlier_dict(self):
        template_dict = {}

        fig_data, filtered_df = self.__prepare_outliers()

        # filtered_df could be used to save to csv if wanted later
        template_dict['operations_dict'] = fig_data['operations_dict']
        template_dict['outliers_list'] = fig_data['outliers_list']
        template_dict['outliers_data'] = fig_data['outliers_data']
        template_dict['outlier_keys'] = ['game_score', 'minutes_played', 'turnovers',
                                         'ast/to', 'personal_fouls', 'defensive_rebounds', 'offensive_rebounds']

        return template_dict

    def __update_graph_and_save(self, save_path):
        df = Api.get_existing_data_frame(csv_path=self.csv_path, logger=logging.getLogger(__name__))
        plot_path, outlier_df, total_df = Api.create_scatter_plot_with_trend_line(x_key=str(self.x_key),
                                                                                  y_key=str(self.y_key),
                                                                                  df=df,
                                                                                  save_path=save_path,
                                                                                  grid=(str(self.grid) != 'Disable'),
                                                                                  trend_line=(str(
                                                                                      self.trend_line) != 'Disable'),
                                                                                  num_outliers=self.outlier_count,
                                                                                  teams=[str(self.team)],
                                                                                  min_seconds=self.min_seconds,
                                                                                  max_seconds=self.max_seconds)
        return plot_path, outlier_df, total_df

    def __prepare_outliers(self):
        """
        Gets the svg code for the desired plot.

        :return: outlier data
        :rtype: dict
        """
        df = Api.get_existing_data_frame(csv_path=self.csv_path, logger=logging.getLogger(__name__))

        plot_path, outlier_df, total_df = self.__update_graph_and_save(save_path=None)
        describe_dict = total_df.describe().to_dict()
        describe_dict = describe_dict[str(self.y_key)]
        operations_dict = OrderedDict()
        operations_dict['(Percentiles)'] = ''
        for k, v in sorted(describe_dict.items()):
            operations_dict['%s:' % k] = round(v, 3)
        outliers_data = []
        outliers_list = []
        for _, row in outlier_df.sort_values(by=str(self.y_key), ascending=False).iterrows():
            outliers_data.append(self.__fix_outlier_dict(row_series=row, df=df))
        outlier_str = outlier_df[[str(self.y_key)]].sort_values(by=str(self.y_key), ascending=False).to_string()
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
            'operations_dict': operations_dict,
            'outliers_list': outliers_list,
            'outliers_data': outliers_data,
        }

        # todo update to properly check if plot is none?
        return figure_dict, total_df

    def __fix_outlier_dict(self, row_series, df):
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
        date = self.__convert_date(row_series['date'])
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

    @staticmethod
    def __convert_date(date_string):
        """
        Gets a datetime object from a date string.

        :param date_string: The date string
        :return: datetime.datetime object
        """
        return datetime.datetime.strptime(date_string, '%y_%m_%d')
