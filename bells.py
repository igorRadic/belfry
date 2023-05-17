import RPi.GPIO as GPIO
from multiprocessing import Queue

# use Raspberry Pi 4B board pin numbers
GPIO.setmode(GPIO.BCM)

# Set GPIO pins for bells
BELL_A = 26
BELL_B = 19
BELL_C = 13
BELL_D = 6
"""
Bell A is the largest, bell D is the smallest
"""

bell_programs = [
    # Every day
    {
        "name": "Svaki dan: 12h",
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": [12],  # start hour
        "minute": [00],  # start minute
        "day": [0, 1, 2, 3, 4, 5, 6],  # Every day
        "duration": 120,  # [s]
    },
    {
        "name": "Svaki dan: 20h",
        "bells": [BELL_A, BELL_D],
        "hour": [20],  # start hour
        "minute": [00],  # start minute
        "day": [0, 1, 2, 3, 4, 5, 6],  # Every day
        "duration": 120,  # [s]
    },
    # Work day
    {
        "name": "Radni dan: 15 do večernje mise",
        "bells": [BELL_C],
        "hour": [18],  # start hour
        "minute": [15],  # start minute
        "day": [0, 1, 2, 3, 4, 5],  # Work day
        "duration": 120,  # [s]
    },
    # Sunday
    {
        "name": "Nedjelja: 15 do jutarnje mise",
        "bells": [BELL_C],
        "hour": [6],  # start hour
        "minute": [45],  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "Nedjelja: 5 do jutarnje mise",
        "bells": [BELL_B, BELL_C],
        "hour": [6],  # start hour
        "minute": [55],  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "Nedjelja: 15 do župne mise",
        "bells": [BELL_C],
        "hour": [9],  # start hour
        "minute": [45],  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "Nedjelja: 5 do župne mise",
        "bells": [BELL_B, BELL_C],
        "hour": [9],  # start hour
        "minute": [55],  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "Nedjelja: 15 do večernje mise",
        "bells": [BELL_C],
        "hour": [18],  # start hour
        "minute": [15],  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "Nedjelja: 5 do večernje mise",
        "bells": [BELL_B, BELL_C],
        "hour": [18],  # start hour
        "minute": [25],  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    # Other
    {
        "name": "Sprovod 12:30",
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": [12],  # start hour
        "minute": [30],  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "Sprovod 12:55",
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": [12],  # start hour
        "minute": [55],  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "Sprovod 14:30",
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": [14],  # start hour
        "minute": [30],  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "Sprovod 14:55",
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": [14],  # start hour
        "minute": [55],  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
]

# set up the GPIO modes
output_pins = [BELL_A, BELL_B, BELL_C, BELL_D]
for out in output_pins:
    GPIO.setup(out, GPIO.OUT)
