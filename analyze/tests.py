from django.test import TestCase
from .models import TeamGraph
from .constants import Defaults as Vars
import os
import tempfile
import shutil


class GraphModelTests(TestCase):
    def setUp(self):
        self.test_graph = TeamGraph(x_key=Vars.x_key,
                                    y_key=Vars.y_key,
                                    team=Vars.team,
                                    trend_line=Vars.trend,
                                    grid=Vars.grid)
        media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Media')
        os.mkdir(os.path.join(media_dir, 'Temp'))
        self.logs_dir = os.path.join(media_dir, 'Temp')

    def tearDown(self):
        if os.path.exists(self.logs_dir):
            shutil.rmtree(self.logs_dir)

    def test_get_svg_text_nominal(self):
        """
        The Graph method `get_svg_text` shall return a string greater than 100 characters. This should mostly test that
        this works.
        """
        self.assertTrue('svg' in self.test_graph.get_svg_text())

    def test_create_png_location_nominal(self):
        """
        The Graph method `get_svg_text` shall
        """
        plot_location = os.path.join(self.logs_dir, 'minutes_played_vs_points_min_0_max_6000.png')
        ret_loc = self.test_graph.create_png_location(save_dir=self.logs_dir)
        self.assertEqual(ret_loc, plot_location)
        self.assertTrue(os.path.exists(plot_location))
