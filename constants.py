

class Defaults(object):
    x_key = 'minutes_played'
    y_key = 'points'
    team = 'Los Angeles Lakers'
    grid = 'Enable'
    trend = 'Enable'
    min_seconds = 0
    max_seconds = 6000
    outliers = 5


class ScatterFilters(object):
    x_keys = sorted(['minutes_played', 'seconds_played'])
    y_keys = sorted(['points', 'rebounds', 'assists', 'made_field_goals', 'made_three_point_field_goals',
                     'made_free_throws', 'offensive_rebounds', 'defensive_rebounds', 'attempted_field_goals',
                     'attempted_three_point_field_goals', 'attempted_free_throws', 'steals', 'blocks',
                     'turnovers', 'game_score', 'true_shooting', 'assist_turnover_ratio'])
    teams = sorted(['Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
                    'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons',
                    'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers', 'Los Angeles Clippers',
                    'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat', 'Milwaukee Bucks',
                    'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks', 'Oklahoma City Thunder',
                    'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trailblazers', 'Sacramento Kings',
                    'San Antonio Spurs', 'Toronto Raptors'])
    grid_choices = ['Enable', 'Disable']
    trend_choices = ['Enable', 'Disable']
