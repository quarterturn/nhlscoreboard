import datetime
import time
import os
import requests
from lib import nhl
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import random
from PIL import Image

class scoreboard(object):
    def __init__(self):
        super(scoreboard, self).__init__()

    def sleep(self, sleep_period):
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


    def setup_nhl(self):
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
        settings_file = '/home/pi/nhlscoreboard/settings.txt'
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


    def run(self):

        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 4
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat-pwm"
        options.pixel_mapper_config = "U-mapper"
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 8
        options.brightness = 100
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = "RBG"
        options.show_refresh_rate = 0
        options.gpio_slowdown = 1
        self.matrix = RGBMatrix(options = options)

        white = graphics.Color(255, 255, 255)
        gray = graphics.Color(127, 127, 127)
        green = graphics.Color(0, 150, 0)
        yellow = graphics.Color(127, 127, 0)
        red = graphics.Color(150, 0, 0)
        blue = graphics.Color(0, 0, 150)
        magenta = graphics.Color(127, 0, 127)
        cyan = graphics.Color(0, 127, 127)
        dim = graphics.Color(10, 10, 10)

        
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()

        #main_dir = os.getcwd()
        main_dir = "/home/pi/nhlscoreboard"

        width = 128
        height = 64
        font_medium = graphics.Font()
        font_medium.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/7x13.bdf")
        font_small = graphics.Font()
        font_small.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/6x10.bdf")
        font_big = graphics.Font() 
        font_big.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/9x15.bdf")

        fontYoffset = 8
        fontYoffset2 = 8
        x_offset = -64

        gameday = False
        season = False
        home_score = 0
        home_score_old = 0
        away_score = 0
        away_score_old = 0
        home_team = ""
        away_team = ""
        live_stats_link = ""
        x = 0
        y =10 
        home_score_color = ""
        away_score_color = ""
        do_once = 1
        ignore_first_score_change = 1

        random.seed()
        choice = 1

        teams = {1 : "NJD", 2 : "NYI", 3 : "NYR", 4 : "PHI", 5 : "PIT", 6 : "BOS", 7 : "BUF", 8 : "MTL", 9 : "OTT", 10 : "TOR", 12 : "CAR", 13 : "FLA", 14 : "TBL", 15 : "WSH", 16 : "CHI", 17 : "DET", 18 : "NSH", 19 : "STL", 20 : "CGY", 21 : "COL", 22 : "EDM", 23 : "VAN", 24 : "ANA", 25 : "DAL", 26 : "LAK", 28 : "SJS", 29 : "CBJ", 30 : "MIN", 52 : "WPG", 53 : "ARI", 54 : "VGK"}
        team_id, delay = self.setup_nhl()

        #image = Image.open("/home/pi/nhlscoreboard/images/goal.png")
        #self.matrix.SetImage(image.convert('RGB'))
        #time.sleep(5)

        try:

            while (True):

                time.sleep(5)

                # check if in season
                season = nhl.check_season()
                if season:

                    # check game
                    gameday = nhl.check_if_game(team_id)

                    if gameday:

                        # check end of game
                        game_end = nhl.check_game_end(team_id)

                        if not game_end:
                            try:
                                # get score, teams, and live stats link
                                home_score, home_team, away_score, away_team, live_stats_link = nhl.fetch_game(team_id)
                            except TypeError:
                                continue

                            # get stats from the game
                            current_period, home_sog, away_sog, home_powerplay, away_powerplay, time_remaining = nhl.fetch_live_stats(live_stats_link)
                            # the the rosters just once at the start
                            if do_once:
                                home_roster, away_roster = nhl.fetch_rosters(live_stats_link)
                                do_once = 0

                            if current_period > 0:
    
                                # get the players on ice
                                home_on_ice, away_on_ice = nhl.players_on_ice(live_stats_link)
                                # build a list like so for each team
                                # jersey_number lastname
                                home_ice_list = []
                                away_ice_list = []
                                home_goalie_id, away_goalie_id = nhl.fetch_goalies(live_stats_link)
                                for the_id in home_on_ice:
                                    try:
                                        jersey_number = (home_roster['ID'+str(the_id)]['jerseyNumber']).encode("ascii")
                                    except:
                                        jersey_number = "0"
                                    if int(jersey_number) < 10:
                                        try:
                                            jersey_number = jersey_number.decode("utf-8") + ' '
                                        except:
                                            jersey_number = '00' 
                                    else:
                                        try:
                                            jersey_number = jersey_number.decode("utf-8")
                                        except:
                                            jersey_number = '00'

                                    last_name = (((home_roster['ID'+str(the_id)]['person']['fullName']).split(' ', 1))[1]).encode("ascii")
                                    temp_thing = jersey_number + ' ' + (last_name[0:7].upper()).decode("utf-8")
                                    home_ice_list.append(temp_thing)
                                for the_id in away_on_ice:
                                    jersey_number = (away_roster['ID'+str(the_id)]['jerseyNumber']).encode("ascii")
                                    if int(jersey_number) < 10:
                                        jersey_number = jersey_number.decode("ascii") + ' '
                                    else:
                                        jersey_number = jersey_number.decode("utf-8")
                                    last_name = (((away_roster['ID'+str(the_id)]['person']['fullName']).split(' ', 1))[1]).encode("ascii")
                                    temp_thing = jersey_number + ' ' + (last_name[0:7].upper()).decode("utf-8")
                                    away_ice_list.append(temp_thing)
    
                                # determine score colors
                                if home_score > away_score:
                                    home_score_color = red
                                    away_score_color = green
                                elif away_score > home_score:
                                    home_score_color = green
                                    away_score_color = red
                                else:
                                    home_score_color = green
                                    away_score_color = green
    
                                # determine team colors
                                if home_powerplay == 1:
                                    home_team_color = yellow
                                else:
                                    home_team_color = gray
                                if away_powerplay == 1:
                                    away_team_color = yellow
                                else:
                                    away_team_color = gray 
    
    
                                # reset x and y
                                x = 0
                                y = 0
        
                                # clear the offscreen canvas
                                offscreen_canvas.Clear() 

                                # teams
                                # away on left
                                # home on right
                                # 3-letter team, score, sog
                                graphics.DrawText(offscreen_canvas, font_small, 0, y + fontYoffset, away_team_color, teams[away_team])
                                graphics.DrawText(offscreen_canvas, font_small, 28, y + fontYoffset, away_score_color, str(away_score))
                                graphics.DrawText(offscreen_canvas, font_small, 49, y + fontYoffset, yellow, str(away_sog))
                                y += 8
                                # players on ice
                                for line in away_ice_list:
                                    graphics.DrawText(offscreen_canvas, font_small, 0, y + fontYoffset, gray, line)
                                    y += 8
        
                                # away on left
                                y = 0
                                # 3-letter team, score, sog
                                graphics.DrawText(offscreen_canvas, font_small, 64, y + fontYoffset, home_team_color, teams[home_team])
                                graphics.DrawText(offscreen_canvas, font_small, 92, y + fontYoffset, home_score_color, str(home_score))
                                graphics.DrawText(offscreen_canvas, font_small, 113, y + fontYoffset, yellow, str(home_sog))
                                y += 8
                                # players on ice
                                for line in home_ice_list:
                                    graphics.DrawText(offscreen_canvas, font_small, 64, y + fontYoffset, gray, line)
                                    y += 8
        
                                y = 64
                                status, time_remaining = nhl.intermission_status(live_stats_link)
                                if status == False:
                                    graphics.DrawText(offscreen_canvas, font_small, 35, y, cyan, "PERIOD: " + str(current_period))
                                else:
                                    m, s = divmod(time_remaining, 60)
                                    graphics.DrawText(offscreen_canvas, font_small, 0, y, cyan, "INTERMISSION " + '{:02d}:{:02d}'.format(m, s))
                                # blit it to the screen  
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
    
                                # If score change...
                                if home_score > home_score_old:
                                    home_score_old = home_score
                                    choice = random.randint(1,3)    
                                    if ignore_first_score_change == 0:
                                        if home_team == int(team_id):
                                            time.sleep(delay)
                                            image = Image.open("/home/pi/nhlscoreboard/images/goal.png")
                                            self.matrix.SetImage(image.convert('RGB'))
                                            time.sleep(5)
                                    else:
                                        ignore_first_score_change = 0
                                else:
                                    home_score_old = home_score

                                # If score change...
                                if away_score > away_score_old:
                                    away_score_old = away_score
                                    choice = random.randint(1,3)    
                                    if ignore_first_score_change == 0:
                                        if away_team == int(team_id):
                                            time.sleep(delay)
                                            image = Image.open("/home/pi/nhlscoreboard/images/goal.png")
                                            self.matrix.SetImage(image.convert('RGB'))
                                            time.sleep(5)
                                    else:
                                        ignore_first_score_change = 0
                                            
                                else:
                                    away_score_old = away_score

                                ignore_first_score_change = 0

                            if current_period == 0:
                               offscreen_canvas.Clear()
                               y = 7
                               x_offset = x_offset + 1
                               if x_offset > 128:
                                   x_offset = -128
                               graphics.DrawText(offscreen_canvas, font_small, x + x_offset, y, blue, "GAME TODAY!")
                               y += fontYoffset2
                               graphics.DrawText(offscreen_canvas, font_small, x + 10 + x_offset, y, green, "GAME TODAY!")
                               y += fontYoffset2
                               graphics.DrawText(offscreen_canvas, font_small, x + 20 + x_offset, y, red, "GAME TODAY!")
                               y += fontYoffset2
                               graphics.DrawText(offscreen_canvas, font_small, x + 30 + x_offset, y, yellow, "GAME TODAY!")
                               y += fontYoffset2
                               graphics.DrawText(offscreen_canvas, font_small, x + 40 + x_offset, y, magenta, "GAME TODAY!")
                               y += fontYoffset2
                               graphics.DrawText(offscreen_canvas, font_small, x + 50 + x_offset, y, cyan, "GAME TODAY!")
                               y += fontYoffset2
                               temptime = datetime.datetime.now()
                               graphics.DrawText(offscreen_canvas, font_small, 0, y, gray, temptime.strftime("%m/%d/%y %H:%M")) 
                               y += fontYoffset2
                               game_start_time = nhl.fetch_game_start_time(live_stats_link)
                               graphics.DrawText(offscreen_canvas, font_small, 0, y, gray, "GAMETIME: " + game_start_time)
                               offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                               

                        else:
                            old_score = 0 # Reset for new game
                            self.matrix.Clear()
                            offscreen_canvas.Clear()
                            do_once = 1
                            self.sleep("day")  # sleep till tomorrow
                    else:
                        print("No Game Today!")
                        self.sleep("day")  # sleep till tomorrow
                else:
                    print("OFF SEASON!")
                    self.sleep("season")  # sleep till next season

        except KeyboardInterrupt:
            print("\nCtrl-C pressed")

if __name__ == "__main__":
    my_scoreboard = scoreboard()
    try:
        # Start loop
        print("Press CTRL-C to stop")
        my_scoreboard.run()
    except KeyboardInterrupt:
        print("Exiting\n")
        sys.exit(0)

