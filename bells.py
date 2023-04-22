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
    {
        "name": "Nedjelja: 15 do mise",
        "bells": [BELL_A, BELL_B],
        "hour": [6],  # start hour
        "minute": [45],  # start minute
        "day": [6],  # sunday
        "duration": 120,  # [s]
    }
]

# set up the GPIO modes
output_pins = [BELL_A, BELL_B, BELL_C, BELL_D]
for out in output_pins:
    GPIO.setup(out, GPIO.OUT)
