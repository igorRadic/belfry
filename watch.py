"""Module for watch manipulation.

The watch has only hour and minute handle,
this module manipulates the GPIO pins which then
manipulate relays that turn on and off
electric motors on which are handles.
There are two GPIO pins, each for one handle, 
according to that there arealse  two electric motors.
"""

import RPi.GPIO as GPIO
from utils import delay
from time import perf_counter
import datetime
import multiprocessing

# use Raspberry Pi 4B board pin numbers
GPIO.setmode(GPIO.BCM)

# Set GPIO pins for watch handles
MINUTE_HANDLE = 23
HOUR_HANDLE = 24

# set up GPIO pin modes
for pin in [MINUTE_HANDLE, HOUR_HANDLE]:
    GPIO.setup(pin, GPIO.OUT)

# Declare how long to move each handle
# and when to start moving handles
MINUTE_HANDLE_DELAY = 3.1  # [s]
HOUR_HANDLE_DELAY = 3.1  # [s]

MINUTE_HANDLE_START = 57  # [s]
HOUR_HANDLE_START = 2  # [s]

ONE_SECOND = 1


def move_minute_handle():
    """
    This function sets GPIO pin to HIGH which turns on electric motor.
    Minute handle moves as long as the GPIO pin is in HIGH state.
    """
    print("-=--=- start moving: Minute handle  -=--=-")
    GPIO.output(MINUTE_HANDLE, GPIO.HIGH)
    delay(seconds=MINUTE_HANDLE_DELAY)
    GPIO.output(MINUTE_HANDLE, GPIO.LOW)
    print("-=--=- stop moving: Minute handle  -=--=-")


def move_hour_handle():
    """
    This function sets GPIO pin to HIGH which turns on electric motor.
    Hour handle moves as long as the GPIO pin is in HIGH state.
    """
    print("-=- start moving: Hour handle -=-")
    GPIO.output(HOUR_HANDLE, GPIO.HIGH)
    delay(HOUR_HANDLE_DELAY)
    GPIO.output(HOUR_HANDLE, GPIO.LOW)
    print("-=- stop moving: Hour handle  -=-")


def watch(message_queue: multiprocessing.Queue):
    """This function is main watch function.

    It sends tick to other processes every second and
    it starts moving handles when it is time for it.
    """
    while True:
        # Get current date and time
        loop_start_time = perf_counter()
        current_datetime = datetime.datetime.now()
        message_queue.put(f"{current_datetime.strftime('%d/%m/%y %H:%M:%S')}")

        # Check if is it time for minute handle moving, if it is, move minute handle
        if int(current_datetime.strftime("%S")) == MINUTE_HANDLE_START:
            seconds_handle_process = multiprocessing.Process(target=move_minute_handle)
            seconds_handle_process.start()

        # Check if is it time for hour handle moving, if it is, move hour handle
        if int(current_datetime.strftime("%S")) == HOUR_HANDLE_START:
            hour_handle_process = multiprocessing.Process(target=move_hour_handle)
            hour_handle_process.start()

        # Wait until next second
        execution_time = perf_counter() - loop_start_time
        if execution_time < ONE_SECOND:
            while perf_counter() < loop_start_time + ONE_SECOND:
                pass
