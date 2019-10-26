import datetime
import time
import os
import requests
from lib import nhl
import atexit
import Image
import ImageDraw
import ImageFont
import os
import time
from rgbmatrix import Adafruit_RGBmatrix

#main_dir = os.getcwd()
main_dir = "/home/alex/nhl_scoreboard"

white = (255, 255, 255)
gray = (127, 127, 127)
green = (  0, 255,   0)
yellow = (127, 127,   0)
red = (255,   0,   0)
blue = (  0,   0, 255)

width = 64
height = 32
matrix = Adafruit_RGBmatrix(32, 2) # rows, chain length
font = ImageFont.load(os.path.dirname(os.path.realpath(__file__)) + '/helvR08.pil')
font_small = ImageFont.load(os.path.dirname(os.path.realpath(__file__)) + '/helvR06.pil')
font_big = ImageFont.load(os.path.dirname(os.path.realpath(__file__))
                   + '/helvR10.pil')

fontYoffset = -2  # Scoot up a couple lines so descenders aren't cropped

# Drawing takes place in offscreen buffer to prevent flicker
image       = Image.new('RGB', (width, height))
draw        = ImageDraw.Draw(image)

# Clear matrix on exit.  Otherwise it's annoying if you need to break and
# fiddle with some code while LEDs are blinding you.
def clearOnExit():
	matrix.Clear()

atexit.register(clearOnExit)

# Clear background
draw.rectangle((0, 0, width, height), fill=(0, 0, 0))

def sleep(sleep_period):
    """ Function to sleep if not in season or no game.
    Inputs sleep period depending if it's off season or no game."""

    # Get current time
    now = datetime.datetime.now()
    # Set sleep time for no game today
    if "day" in sleep_period:
        delta = datetime.timedelta(hours=12)
    # Set sleep time for not in season
    elif "season" in sleep_period:
        # If in August, 31 days else 30
        if now.month is 8:
            delta = datetime.timedelta(days=31)
        else:
            delta = datetime.timedelta(days=30)
    next_day = datetime.datetime.today() + delta
    next_day = next_day.replace(hour=12, minute=10)
    sleep = next_day - now
    sleep = sleep.total_seconds()
    time.sleep(sleep)


def setup_nhl():
    """Function to setup the nhl_goal_light.py with team,
    team_id and delay"""

    """Try to find a settings.txt file in the folder to automaticly setup
    the goal light with pre-desired team and delay.
    settings.txt file should as such : Enter team_id and delay,
    each on a separate line in this order. LEAVE EMPTY if you want to
    manually input every time. If program can't find settings.txt file or if
    file is empty, it will ask for user input.
    """
    
    lines = ""
    team = ""
    team_id = ""
    settings_file = '{0}/settings.txt'.format(main_dir)
    if os.path.exists(settings_file):
        # get settings from file
        f = open(settings_file, 'r')
        lines = f.readlines()
    

    # find team_id
    try:
        team_id = lines[1].strip('\n')
    except IndexError:
        team_id = ""
    if team_id == "":
        team = input("Enter team you want to setup (without city) (Default: Canadiens) \n")
        if team == "":
            team = "Canadiens"
        else:
            team = team.title()

        # query the api to get the ID
        team_id = nhl.get_team_id(team)

    # find delay
    try:
        delay = lines[2].strip('\n')
    except IndexError:
        delay = ""
    if delay is "":
        delay = input("Enter delay required to sync : \n")
        if delay is "":
            delay = 0
    delay = float(delay)
    delay = 0.0
    
    return (team_id, delay)


if __name__ == "__main__":

    old_score = 0
    new_score = 0
    gameday = False
    season = False
    home_score = 0
    away_score = 0 
    home_team = ""
    away_team = ""
    live_stats_link = ""
    x = 0
    y = 0
    home_score_color = ""
    away_score_color = ""
    do_once = 1
 
    teams = {1 : "NJD", 2 : "NYI", 3 : "NYR", 4 : "PHI", 5 : "PIT", 6 : "BOS", 7 : "BUF", 8 : "MTL", 9 : "OTT", 10 : "TOR", 12 : "CAR", 13 : "FLA", 14 : "TBL", 15 : "WSH", 16 : "CHI", 17 : "DET", 18 : "NSH", 19 : "STL", 20 : "CGY", 21 : "COL", 22 : "EDM", 23 : "VAN", 24 : "ANA", 25 : "DAL", 26 : "LAK", 28 : "SJS", 29 : "CBJ", 30 : "MIN", 52 : "WPG", 53 : "ARI", 54 : "VGK"}
    team_id, delay = setup_nhl()

    try:

        while (True):

            time.sleep(1)
            
            # check if in season
            season = nhl.check_season()
            if season:

                # check game
                gameday = nhl.check_if_game(team_id)

                if gameday:
                    
                    # check end of game
                    game_end = nhl.check_game_end(team_id)
                    
                    if not game_end:
            
                        # Check score online and save score
                        new_score = nhl.fetch_score(team_id)

                        # new function fetch_game(team_id)
                        # returns home_score, home_team, away_score, away_team
                        try:
                            home_score, home_team, away_score, away_team, live_stats_link = nhl.fetch_game(team_id)
                        except TypeError:
                            continue
                        #print("Home team: {0} Home score: {1} Away team: {2} Away score: {3}".format( teams[home_team], home_score, teams[away_team], away_score)) 

                        # get stats from the game
                        current_period, home_sog, away_sog, home_powerplay, away_powerplay, time_remaining = nhl.fetch_live_stats(live_stats_link) 
                        # the the rosters just once at the start
                        if do_once:
                            home_roster, away_roster = nhl.fetch_rosters(live_stats_link)
                            do_once = 0
                        
                        # get the players on ice
                        home_on_ice, away_on_ice = nhl.players_on_ice(live_stats_link) 
                        # build a list like so for each team
                        # jersey_number lastname
                        home_ice_list = []
                        away_ice_list = []
                        for the_id in home_on_ice:
                            jersey_number = (home_roster['ID'+str(the_id)]['jerseyNumber']).encode("ascii")
                            if (int(jersey_number)) < 10:
                                jersey_number = ' ' + jersey_number
                            # hopefully all the names are first last
                            # if not we will have to count the list from split and take the last one
                            last_name = (((home_roster['ID'+str(the_id)]['person']['fullName']).split(' ', 1))[1]).encode("ascii")
                            home_ice_list.append(jersey_number+' '+last_name.upper())
                        for the_id in away_on_ice:
                            jersey_number = (away_roster['ID'+str(the_id)]['jerseyNumber']).encode("ascii")
                            if (int(jersey_number)) < 10:
                                jersey_number = '  ' + jersey_number
                            last_name = (((away_roster['ID'+str(the_id)]['person']['fullName']).split(' ', 1))[1]).encode("ascii")
                            away_ice_list.append(jersey_number+' '+last_name.upper())
                            

                        # determine score colors
                        if home_score > away_score:
                            home_score_color = (200,   0,   0)
                            away_score_color = (  0, 200,   0)
                        elif away_score > home_score:
                            home_score_color = (  0, 200,   0)
                            away_score_color = (200,   0,   0)
                        else:
                            home_score_color = green
                            away_score_color = green 
                        
                        # determine team colors
                        if home_powerplay == 1:
                            home_team_color = (127, 127, 0)
                        else:
                            home_team_color = (127, 127, 127)
                        if away_powerplay == 1:
                            away_team_color = (127, 127, 0)
                        else:
                            away_team_color = (127, 127, 127)


			# clear the buffer
                        draw.rectangle((0, 0, width, height), fill=(0, 0, 0))

                        # reset x and y
                        x = 0
                        y = 0

#			# teams
#			draw.text((x, y + fontYoffset),
#						  teams[away_team], font=font, fill=away_team_color)
#                        # x += font.getsize(teams[home_team])[0]
#                        x = 40 
#			draw.text((x, y + fontYoffset),
#						  teams[home_team], font=font, fill=home_team_color)
#                        x = 0
#                        y += 11 
#
#                        # scores
#                        x += 8
#                        draw.text((x, y + fontYoffset),
#                                                  str(away_score), font=font_big, fill=away_score_color)
#                        x = 40 
#                        x += 8 
#                        draw.text((x, y + fontYoffset),
#                                                  str(home_score), font=font_big, fill=home_score_color)
#                        # shots on goal
#                        x = 4
#                        y = 24
#                        draw.text((x, y + fontYoffset), str(away_sog), font=font_small, fill=gray)
#                        x = 40 
#                        x += 8
#                        draw.text((x, y + fontYoffset), str(home_sog), font=font_small, fill=gray)
#                        x -= 28
#                        # time remaining in period
#                        draw.text((x, y + fontYoffset), str(time_remaining), font=font_small, fill=yellow)
#
#                        # period
#                        y = 15
#                        x = 28
#                        draw.text((x, y + fontYoffset), str(current_period), font=font_small, fill=yellow)
                        if team_id == home_team:
                            for line in home_ice_list:
                                draw.text((x, y + fontYoffset), line, font=font_small, fill=gray) 
                                y += 7
                        else:
                            for line in away_ice_list:
                                draw.text((x, y + fontYoffset), line, font=font_small, fill=gray)
                                y += 7
       
                        # copy the buffer to the screen
                        matrix.SetImage(image.im.id, 0, 0)


                        # If score change...
                        if new_score != old_score:
                            time.sleep(delay) 
                            if new_score > old_score:
                                # save new score
                                print("GOAL!")
                                # activate_goal_light()
                            old_score = new_score
                            

                    else:
                        print("Game Over!")
                        old_score = 0 # Reset for new game
                        do_once = 1
                        sleep("day")  # sleep till tomorrow
                else:
                    print("No Game Today!")
                    sleep("day")  # sleep till tomorrow
            else:
                print("OFF SEASON!")
                sleep("season")  # sleep till next season

    except KeyboardInterrupt:
        print("\nCtrl-C pressed")
