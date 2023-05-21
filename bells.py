"""Module which manipultes with bells.

It starts ringing when it is time for it.
"""

import datetime
import multiprocessing

import RPi.GPIO as GPIO

from utils import delay

# Use Raspberry Pi 4B board pin numbers.
GPIO.setmode(GPIO.BCM)

# Ignore GPIO warnings.
GPIO.setwarnings(False)

# Set GPIO pins for bells.
BELL_A = 6
BELL_B = 13
BELL_C = 19
BELL_D = 26
"""
Bell A is the largest, bell D is the smallest
"""

# Set up the GPIO modes.
output_pins = [BELL_A, BELL_B, BELL_C, BELL_D]
for out in output_pins:
    GPIO.setup(out, GPIO.OUT)

"""
Bell programs are presets for ringing, in bell program
is described when to ring, how long to ring, whether function
button activates program and which bells should ring.

To add new bell program add new element in this dict.
"""
bell_programs = [
    # Every day
    {
        "name": "Podne",
        "function_button": None,
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 12,  # start hour
        "minute": 00,  # start minute
        "day": [0, 1, 2, 3, 4, 5, 6],  # Every day
        "duration": 120,  # [s]
    },
    {
        "name": "20:00h",
        "function_button": None,
        "bells": [BELL_A, BELL_D],
        "hour": 20,  # start hour
        "minute": 00,  # start minute
        "day": [0, 1, 2, 3, 4, 5, 6],  # Every day
        "duration": 120,  # [s]
    },
    # Work day
    {
        "name": "15 do mise",
        "function_button": None,
        "bells": [BELL_C],
        "hour": 18,  # start hour
        "minute": 15,  # start minute
        "day": [0, 1, 2, 3, 4, 5],  # Work day
        "duration": 120,  # [s]
    },
    # Sunday
    {
        "name": "15 do mise",
        "function_button": None,
        "bells": [BELL_C],
        "hour": 6,  # start hour
        "minute": 45,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "5 do mise",
        "function_button": None,
        "bells": [BELL_B, BELL_C],
        "hour": 6,  # start hour
        "minute": 55,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "15 do mise",
        "function_button": None,
        "bells": [BELL_C],
        "hour": 9,  # start hour
        "minute": 45,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "5 do mise",
        "function_button": None,
        "bells": [BELL_B, BELL_C],
        "hour": 9,  # start hour
        "minute": 55,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "15 do mise",
        "function_button": None,
        "bells": [BELL_C],
        "hour": 18,  # start hour
        "minute": 15,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    {
        "name": "5 do mise",
        "function_button": None,
        "bells": [BELL_B, BELL_C],
        "hour": 18,  # start hour
        "minute": 25,  # start minute
        "day": [6],  # Sunday
        "duration": 120,  # [s]
    },
    # Other
    {
        "name": "30 do sprovoda",
        "function_button": 0,  # Function button 0 activates this program
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 12,  # start hour
        "minute": 30,  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "5 do sprovoda",
        "function_button": 0,  # Function button 0 activates this program
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 12,  # start hour
        "minute": 55,  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "30 do sprovoda",
        "function_button": 1,  # Function button 1 activates this program
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 14,  # start hour
        "minute": 30,  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
    {
        "name": "5 do sprovoda",
        "function_button": 1,  # Function button 0 activates this program
        "bells": [BELL_A, BELL_B, BELL_C, BELL_D],
        "hour": 14,  # start hour
        "minute": 55,  # start minute
        "day": [],  # Only when activated
        "duration": 120,  # [s]
    },
]


def convert_pin_to_bell_name(pin: int) -> str:
    if pin == BELL_A:
        return "A"
    elif pin == BELL_B:
        return "B"
    elif pin == BELL_C:
        return "C"
    elif pin == BELL_D:
        return "D"


def parse_bell_program_for_display(bell_program: dict) -> str:
    """
    This function parses and adjuts output message for 16x2 display.
    """
    message_for_display = (
        bell_program["name"] + " " * (16 - len(bell_program["name"])) + " "
    )
    for bell in bell_program["bells"]:
        message_for_display = message_for_display + convert_pin_to_bell_name(bell)
    return message_for_display


def ring(program: dict, message_queue: multiprocessing.Queue) -> None:
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
    # Notify the parent process that ringing is complete.
    message_queue.put(f"Stop ringing")


def bells(
    current_datetime_queue_in: multiprocessing.Queue,
    states_queue_in: multiprocessing.Queue,
    message_queue_for_display: multiprocessing.Queue,
) -> None:
    """This is main bell function.

    It calls bell ringing.
    """
    function_buttons_states = [False, False]

    while True:
        if not current_datetime_queue_in.empty():
            recieved_message = current_datetime_queue_in.get()

            # Convert str to datetime.
            current_datetime = datetime.datetime.strptime(
                recieved_message, "%d/%m/%y %H:%M:%S"
            )

            # Go through all programs and check if it is time for ringing.
            for bell_program in bell_programs:
                if not bell_program["day"]:
                    if function_buttons_states[bell_program["function_button"]]:
                        if current_datetime.hour == bell_program["hour"]:
                            if current_datetime.minute == bell_program["minute"]:
                                if current_datetime.second == 0:
                                    multiprocessing.Process(
                                        target=ring,
                                        args=(bell_program, message_queue_for_display),
                                    ).start()
                elif current_datetime.weekday() in bell_program["day"]:
                    if current_datetime.hour == bell_program["hour"]:
                        if current_datetime.minute == bell_program["minute"]:
                            if current_datetime.second == 0:
                                multiprocessing.Process(
                                    target=ring,
                                    args=(bell_program, message_queue_for_display),
                                ).start()
        # Get funciton buttons states on their change.
        if not states_queue_in.empty():
            function_buttons_states = states_queue_in.get()
            print(f"Function button 0 state: {function_buttons_states[0]}.")
            print(f"Function button 1 state: {function_buttons_states[1]}.")
        else:
            continue
