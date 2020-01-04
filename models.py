import logging
import os
from django.db import models
from .NBA_Beautiful_Data.analytics import analytics_API as Api
from mysite import settings


class ScatterXKey(models.Model):
    id = models.AutoField(primary_key=True)
    x_key = models.CharField(max_length=35)

    # Metadata
    class Meta:
        ordering = ['x_key']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.x_key


class ScatterYKey(models.Model):
    id = models.AutoField(primary_key=True)
    y_key = models.CharField(max_length=35)

    # Metadata
    class Meta:
        ordering = ['y_key']

    def __str__(self):
        return self.y_key


class BasketballTeamName(models.Model):
    team_id = models.AutoField(primary_key=True)
    team = models.CharField(max_length=50)

    # Metadata
    class Meta:
        ordering = ['team']

    def __str__(self):
        return self.team


class TrendLineChoice(models.Model):
    trend_id = models.AutoField(primary_key=True)
    choice = models.CharField(max_length=50)

    # Metadata
    class Meta:
        ordering = ['choice']

    def __str__(self):
        return self.choice


class GridChoice(models.Model):
    grid_id = models.AutoField(primary_key=True)
    choice = models.CharField(max_length=50)

    # Metadata
    class Meta:
        ordering = ['choice']

    def __str__(self):
        return self.choice


class Graph(models.Model):
    # SQL fields
    graph_id = models.AutoField(primary_key=True)
    x_key = models.ForeignKey(ScatterXKey, on_delete=models.PROTECT)
    y_key = models.ForeignKey(ScatterYKey, on_delete=models.PROTECT)
    team = models.ForeignKey(BasketballTeamName, on_delete=models.PROTECT)
    trend_line = models.ForeignKey(TrendLineChoice, on_delete=models.PROTECT)
    grid = models.ForeignKey(GridChoice, on_delete=models.PROTECT)
    min_seconds = models.IntegerField(default=0)
    max_seconds = models.IntegerField(default=6000)
    outlier_count = models.IntegerField(default=5)

    # other object vars
    plot_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(settings.BASE_DIR, 'analyze', 'static', 'analyze', 'data', 'player_box_scores.csv')
    png_save_dir = save_path = os.path.join(plot_dir, 'Media', 'Plots')

    def __str__(self):
        return '%s_%s_%s_min_%s_max_%s' % (str(self.x_key), str(self.y_key), self.team, self.min_seconds, self.max_seconds)

    def get_svg_text(self):
        plot_path, _, _ = self.update_graph_and_save(save_path='svg_buffer')
        return plot_path

    def create_png_location(self):
        save_path = os.path.join(self.png_save_dir, '%s_vs_%s_min_%s_max_%s' % (str(self.x_key),
                                                                                str(self.y_key),
                                                                                self.min_seconds,
                                                                                self.max_seconds))
        self.update_graph_and_save(save_path=save_path)
        # there should probably be a check to make sure the graph update worked but for now just assume it did
        return save_path

    def update_graph_and_save(self, save_path):
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
