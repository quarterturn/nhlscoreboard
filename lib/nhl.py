import requests
import datetime

NHL_API_URL = "http://statsapi.web.nhl.com/api/v1/"
NHL_API_URL_BASE = "http://statsapi.web.nhl.com"
#TEST_URL = "http://statsapi.web.nhl.com/api/v1/game/2017020077/feed/live"

def get_teams():
    """ Function to get a list of all the teams name"""

    url = '{0}/teams'.format(NHL_API_URL)
    response = requests.get(url)
    results = response.json()
    teams = []

    for team in results['teams']:
        teams.append(team['franchise']['teamName'])

    return teams


def get_team_id(team_name):
    """ Function to get team of user and return NHL team ID"""

    url = '{0}/teams'.format(NHL_API_URL)
    response = requests.get(url)
    results = response.json()
    teams = []

    for team in results['teams']:
        if team['franchise']['teamName'] == team_name:
            return team['id']

    raise Exception("Could not find ID for team {0}".format(team_name))

def fetch_live_stats(link):
    """ Function to get the live stats of the current game """
    url = '{0}{1}'.format(NHL_API_URL_BASE, link)
    response = requests.get(url)
    stuff = response.json()
    try:
        current_period = int(stuff['liveData']['linescore']['currentPeriod'])
        home_sog = int(stuff['liveData']['linescore']['teams']['home']['shotsOnGoal'])
        away_sog = int(stuff['liveData']['linescore']['teams']['away']['shotsOnGoal'])
        home_powerplay = int(stuff['liveData']['linescore']['teams']['home']['powerPlay'])
        away_powerplay = int(stuff['liveData']['linescore']['teams']['away']['powerPlay'])
        return current_period, home_sog, away_sog, home_powerplay, away_powerplay
    except requests.exceptions.RequestException:
        print("Error encountered getting live stats")
         

def fetch_game(team_id):
    """ Function to get the scores of the game depending on the chosen team.
    Inputs the team ID and returns the score found on web. """

    # Get current time
    now = datetime.datetime.now()

    # Set URL depending on team selected
    url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id)
    # Avoid request errors (might still not catch errors)
    try:
        score = requests.get(url)
        score = score.json()
        home_score = int(score['dates'][0]['games'][0]['teams']['home']['score'])
        home_team = int(score['dates'][0]['games'][0]['teams']['home']['team']['id'])
        away_score = int(score['dates'][0]['games'][0]['teams']['away']['score'])
        away_team = int(score['dates'][0]['games'][0]['teams']['away']['team']['id'])
        live_stats_link = score['dates'][0]['games'][0]['link']
        # Print score for test
        return home_score, home_team, away_score, away_team, live_stats_link
    except requests.exceptions.RequestException:
        print("Error encountered, returning 0 for score")

def fetch_score(team_id):
    """ Function to get the score of the game depending on the chosen team.
    Inputs the team ID and returns the score found on web. """

    # Get current time
    now = datetime.datetime.now()

    # Set URL depending on team selected
    url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id)
    # Avoid request errors (might still not catch errors)
    try:
        score = requests.get(url)
        score = score.json()
        if int(team_id) == int(score['dates'][0]['games'][0]['teams']['home']['team']['id']):
            score = int(score['dates'][0]['games'][0]['teams']['home']['score'])
        else:
            score = int(score['dates'][0]['games'][0]['teams']['away']['score'])

        # Print score for test
        #print("Score: {0} Time: {1}:{2}:{3}".format(score, now.hour, now.minute, now.second))
        return score
    except requests.exceptions.RequestException:
        print("Error encountered, returning 0 for score")
        return 0


def check_season():
    """ Function to check if in season. Returns True if in season, False in off season. """
    # Get current time
    now = datetime.datetime.now()
    if now.month in (7, 8):
        return False
    else:
        return True


def check_if_game(team_id):
    """ Function to check if there is a game now with chosen team. Returns True if game, False if NO game. """

    
    # Set URL depending on team selected
    url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id) #Only shows games after noon, so will sleep till 12:10 pm
    try:
        gameday_url = requests.get(url)
        if "gamePk" in gameday_url.text:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        # Return True to allow for another pass for test
        print("Error encountered, returning True for check_game")
        return True

      
def check_game_end(team_id):
    """ Function to check if the game ofchosen team is over. Returns True if game, False if NO game. """

    # Set URL depending on team selected
    url = '{0}schedule?teamId={1}'.format(NHL_API_URL, team_id)
    # Avoid request errors
    try:
        game_status = requests.get(url)
        game_status = game_status.json()
        game_status = int(game_status['dates'][0]['games'][0]['status']['statusCode'])
        if game_status == 7:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        # Return False to allow for another pass for test
        print("Error encountered, returning False for check_game_end")
        return False
