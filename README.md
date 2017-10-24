# nhlscoreboard


## Overview

NHL team LED matrix scoreboard. Shows the score for your favorite team (and other info) plus whoever they are playing.

Based on code from https://github.com/arim215/nhl_goal_light


Run the following commands manually to install requirements

run:

    $ sudo apt-get install git python python-pip python-dev python-imaging (can use python3 versions if you want)
    $ sudo git clone https://github.com/quarterturn/nhlscoreboard 
    $ sudo pip3 install -r requirements.txt
        

The rpi-rgb-led-matrix library is here: https://github.com/adafruit/rpi-rgb-led-matrix but you should be OK with the provided rgbmatrix.so file.

Edit "settings.txt" file with the following on each line:
team number (see team_dict.py for mapping of teams to numbers)
delay in seconds (to adjust for delay in video transmission)

To start application, use following commands:
	
    $ sudo python nhlscoreboard.py (the code is python3-compatible)

***
### Materials

* Raspberry Pi (B+ or later, if you want to use the Adafruit RGB Matrix HAT)
* Adafruit RGB Matrix HAT (not required but it makes it a lot easier)
* 64x32 LED RGB matrix 
* 8 Amp (or greater) 5v power supply - I used a junkbox ATX power supply modded to run without being attached to a computer
***


