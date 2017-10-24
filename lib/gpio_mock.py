#
# Simple mock object for the GPIO module, allows to test the code
# without executing it on an actual Raspberry Pi
#

BOARD = "BOARD"
IN = "INPUT"
OUT = "OUTPUT"
PUD_DOWN = "PULL_DOWN"
PUD_UP = "PULL_UP"
RISING = "RISING"
FALLING = "FALLING"
LOW = "LOW"
HIGH = "HIGH"

def setmode(mode):
    print("Set mode {0}".format(mode))


def setwarnings(mode):
    print("Set warnings as {0}".format(mode))


def setup(pin,mode,**args):
    print("Set pin {0} as {1} {2}".format(pin, mode,args))


def output(pin, value):
    print("Output {0} to pin {1}".format(value, pin))


def input(pin):
    print("Input 0 to pin {0}".format(pin))
    return 0


def add_event_detect(pin, mode, func, bouncetime):
     print("pin {0}, mode {1}, func {2}, bouncetime {3}".format(pin,mode,func,bouncetime) )


def remove_event_detect(pin):
     print("event detection on pin {0} removed".format(pin))


def cleanup():
     print("Cleanup done")
