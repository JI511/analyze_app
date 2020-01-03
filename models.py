import logging
import os
from django.db import models
from .NBA_Beautiful_Data.analytics import analytics_API as Api


class ScatterXKey(models.Model):
    x_key = models.CharField(max_length=35, primary_key=True)

    # Metadata
    class Meta:
        ordering = ['x_key']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.x_key


class ScatterYKey(models.Model):
    y_key = models.CharField(max_length=35, primary_key=True)

    # Metadata
    class Meta:
        ordering = ['y_key']

    def __str__(self):
        return self.y_key


class BasketballTeamName(models.Model):
    team = models.CharField(max_length=50, primary_key=True)

    # Metadata
    class Meta:
        ordering = ['team']

    def __str__(self):
        return self.team


class TrendLineChoice(models.Model):
    choice = models.CharField(max_length=50, primary_key=True)

    # Metadata
    class Meta:
        ordering = ['choice']

    def __str__(self):
        return self.choice


class GridChoice(models.Model):
    choice = models.CharField(max_length=50, primary_key=True)

    # Metadata
    class Meta:
        ordering = ['choice']

    def __str__(self):
        return self.choice


class Graph(models.Model):
    id = models.IntegerField(primary_key=True)
    x_key = models.ForeignKey(ScatterXKey, on_delete=models.PROTECT)
    y_key = models.ForeignKey(ScatterYKey, on_delete=models.PROTECT)
    team = models.ForeignKey(BasketballTeamName, on_delete=models.PROTECT)
    trend_line = models.ForeignKey(TrendLineChoice, on_delete=models.PROTECT)
    grid = models.ForeignKey(GridChoice, on_delete=models.PROTECT)
    min_seconds = models.IntegerField(default=0)
    max_seconds = models.IntegerField(default=6000)

    def __str__(self):
        name = 'DEFAULT'
        if self.id != 0:
            name = '%s_vs_%s' % (self.x_key, self.y_key)
        return name

    def get_svg_text(self):
        csv_path = os.path.join(os.getcwd(), 'analyze', 'static', 'analyze', 'data', 'player_box_scores.csv')
        df = Api.get_existing_data_frame(csv_path=csv_path, logger=logging.getLogger(__name__))
        outlier_count = 5
        # plot_path will be the svg data as a string
        # total_df will be the filtered df
        plot_path, _, _ = Api.create_scatter_plot_with_trend_line(x_key=self.x_key.__str__(),
                                                                                  y_key=self.y_key.__str__(),
                                                                                  df=df,
                                                                                  save_path='svg_buffer',
                                                                                  grid=(self.grid.__str__() != 'Disable'),
                                                                                  trend_line=(self.trend_line.__str__() != 'Disable'),
                                                                                  num_outliers=outlier_count,
                                                                                  teams=[self.team.__str__()],
                                                                                  min_seconds=self.min_seconds,
                                                                                  max_seconds=self.max_seconds)
        return plot_path

    def create_png_location(self):
        csv_path = os.path.join(os.getcwd(), 'analyze', 'static', 'analyze', 'data', 'player_box_scores.csv')
        df = Api.get_existing_data_frame(csv_path=csv_path, logger=logging.getLogger(__name__))

        outlier_count = 5
        save_path = os.path.join(os.getcwd(), 'analyze', 'static', 'analyze', 'images', 'plot.png')
        # plot_path will be the svg data as a string
        # total_df will be the filtered df
        plot_path, _, _ = Api.create_scatter_plot_with_trend_line(x_key=self.x_key.__str__(),
                                                                  y_key=self.y_key.__str__(),
                                                                  df=df,
                                                                  save_path=save_path,
                                                                  grid=(self.grid.__str__() != 'Disable'),
                                                                  trend_line=(self.trend_line.__str__() != 'Disable'),
                                                                  num_outliers=outlier_count,
                                                                  teams=[self.team.__str__()],
                                                                  min_seconds=self.min_seconds,
                                                                  max_seconds=self.max_seconds)
        return save_path
