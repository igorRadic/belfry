"""Module which manipultes with bells.

It starts ringing when it is time for it.
"""

import RPi.GPIO as GPIO
import multiprocessing
from multiprocessing import Queue
import datetime
from utils import delay

# use Raspberry Pi 4B board pin numbers
GPIO.setmode(GPIO.BCM)

# Set GPIO pins for bells
BELL_A = 6
BELL_B = 13
BELL_C = 19
BELL_D = 26
"""
Bell A is the largest, bell D is the smallest
"""


def convert_pin_to_bell_name(pin: int):
    if pin == BELL_A:
        return "A"
    elif pin == BELL_B:
        return "B"
    elif pin == BELL_C:
        return "C"
    elif pin == BELL_D:
        return "D"


def parse_bell_program_for_display(bell_program: dict):
    message = bell_program["name"] + " " * (16 - len(bell_program["name"])) + " "
    for bell in bell_program["bells"]:
        message = message + convert_pin_to_bell_name(bell)
    return message


bell_programs = [
    # Every day
    {
        "name": "Podne",
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 12,  # start hour
        "minute": 00,  # start minute
        "day": [0, 1, 2, 3, 4, 5, 6],  # Every day
        "duration": 120,  # [s]
    },
    {
        "name": "20:00h",
        "bells": [BELL_A, BELL_D],
        "hour": 20,  # start hour
        "minute": 00,  # start minute
        "day": [0, 1, 2, 3, 4, 5, 6],  # Every day
        "duration": 120,  # [s]
    },
    # Work day
    {
        "name": "15 do mise",
        "bells": [BELL_C],
        "hour": 18,  # start hour
        "minute": 15,  # start minute
        "day": [0, 1, 2, 3, 4, 5],  # Work day
        "duration": 120,  # [s]
    },
    # Sunday
    {
        "name": "15 do mise",
        "bells": [BELL_C],
        "hour": 6,  # start hour
        "minute": 45,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "5 do mise",
        "bells": [BELL_B, BELL_C],
        "hour": 6,  # start hour
        "minute": 55,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "15 do mise",
        "bells": [BELL_C],
        "hour": 9,  # start hour
        "minute": 45,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "5 do mise",
        "bells": [BELL_B, BELL_C],
        "hour": 9,  # start hour
        "minute": 55,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "15 do mise",
        "bells": [BELL_C],
        "hour": 18,  # start hour
        "minute": 15,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "5 do mise",
        "bells": [BELL_B, BELL_C],
        "hour": 18,  # start hour
        "minute": 25,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    # Other
    {
        "name": "30 do sprovoda",
        "function_button": 0,
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 12,  # start hour
        "minute": 30,  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "5 do sprovoda",
        "function_button": 0,
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 12,  # start hour
        "minute": 55,  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "30 do sprovoda",
        "function_button": 1,
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 14,  # start hour
        "minute": 30,  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "5 do sprovoda",
        "function_button": 1,
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 14,  # start hour
        "minute": 55,  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "15 do mise",
        "bells": [BELL_A, BELL_C, BELL_D],
        "hour": 22,  # start hour
        "minute": 25,  # start minute
        "day": [2],  # Only when activated
        "duration": 20,  # [s]
    },
]

# set up the GPIO modes
output_pins = [BELL_A, BELL_B, BELL_C, BELL_D]
for out in output_pins:
    GPIO.setup(out, GPIO.OUT)


def ring(program: dict, message_queue: Queue):
    """
    This function handles ringing as described in program
    passed to it.
    """
    print(f"Start ringing: {program['name']}.")
    message_queue.put(f"Ringing {parse_bell_program_for_display(program)}")
    print(f"Ringing {parse_bell_program_for_display(program)}")

    # Start ringing.
    for bell in program["bells"]:
        GPIO.output(bell, GPIO.HIGH)

    delay(seconds=program["duration"])

    # Stop ringing.
    for bell in program["bells"]:
        GPIO.output(bell, GPIO.LOW)

    print(f"Stop ringing: {program['name']}.")
    message_queue.put(f"Stop ringing")


def bells(current_datetime_queue: Queue, states_queue: Queue, message_queue):
    """This is main bell function.

    It calls bell ringing."""

    function_buttons_state = [False, False]

    while True:
        if not current_datetime_queue.empty():
            recieved_message = current_datetime_queue.get()

            # Convert str to datetime.
            current_datetime = datetime.datetime.strptime(
                recieved_message, "%d/%m/%y %H:%M:%S"
            )

            # Go through all programs and check if it is time for ringing.
            for bell_program in bell_programs:
                if not bell_program["day"]:
                    if function_buttons_state[bell_program["function_button"]]:
                        if current_datetime.hour == bell_program["hour"]:
                            if current_datetime.minute == bell_program["minute"]:
                                if current_datetime.second == 0:
                                    multiprocessing.Process(
                                        target=ring, args=(bell_program, message_queue)
                                    ).start()
                elif current_datetime.weekday() in bell_program["day"]:
                    if current_datetime.hour == bell_program["hour"]:
                        if current_datetime.minute == bell_program["minute"]:
                            if current_datetime.second == 0:
                                multiprocessing.Process(
                                    target=ring, args=(bell_program, message_queue)
                                ).start()
        if not states_queue.empty():
            function_buttons_state = states_queue.get()
            print(function_buttons_state)
        else:
            continue
