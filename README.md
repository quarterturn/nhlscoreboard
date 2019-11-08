# nhlscoreboard


## Overview

NHL team LED matrix scoreboard. Shows the score for your favorite team (and other info) plus whoever they are playing.

Based on code from https://github.com/arim215/nhl_goal_light


Run the following commands manually to install requirements

run:

    sudo apt-get install git python python-pip python-dev python-imaging (can use python3 versions if you want)
    sudo git clone https://github.com/quarterturn/nhlscoreboard 
    curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh >rgb-matrix.sh
    sudo bash rgb-matrix.sh

    cat <<EOF | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf
    blacklist snd_bcm2835
    EOF
    sudo update-initramfs -u   

Edit "settings.txt" file with the following on each line:
team number (see team_dict.py for mapping of teams to numbers)
delay in seconds (to adjust for delay in video transmission)

To start application, use following commands:
	
    $ sudo python nhlscoreboard.py (the code is python3-compatible)

***
### Materials

* Raspberry Pi 3B+ (highly recommended)
* Adafruit RGB Matrix HAT (not required but it makes it a lot easier) with GPIO 4-to-18 wire mode for less flicker.
* 4x 64x32 LED RGB matrix HUB75-type wired in a "U"
* 8 Amp (or greater) 5v power supply - I used a junkbox ATX power supply modded to run without being attached to a computer
***


