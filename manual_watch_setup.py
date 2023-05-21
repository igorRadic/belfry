"""This module 
"""

import datetime
import multiprocessing
import time
from lcd1602 import clear, write
from watch import log_last_watch_time
from function_buttons import F0_BUTTON, F1_BUTTON, F0_LED, F1_LED
from watch import MINUTE_HANDLE, HOUR_HANDLE

import RPi.GPIO as GPIO

# Use Raspberry Pi 4B board pin numbers.
GPIO.setmode(GPIO.BCM)

# Ignore GPIO warnings.
GPIO.setwarnings(False)

# Set GPIO pins
UP_BUTTON = 17
RIGHT_BUTTON = 5
DOWN_BUTTON = 22
LEFT_BUTTON = 27
WATCH_SETUP_SWITCH = 12

buttons = [UP_BUTTON, RIGHT_BUTTON, DOWN_BUTTON, LEFT_BUTTON]

# Set up GPIO pin modes.
for pin in buttons + [WATCH_SETUP_SWITCH]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def is_pressed(button: int) -> bool:
    """This function checks if button (switch) is pressed (on).

    Note: Button (switch) is pressed (on) when input pin is LOW.
    """
    if not GPIO.input(button):
        return True
    else:
        return False


def start_watch_setup(switch: int, watch_setup_state: bool) -> bool:
    """This function checks if watch setup switch is on.

    Note: Manual watch setup starts when switch input pin is LOW and
    watch setup state previously was False.
    """
    if not GPIO.input(switch):
        if watch_setup_state == False:
            return True
    else:
        return False


def manual_watch_setup(
    message_queue_in: multiprocessing.Queue,
    message_queue_for_display: multiprocessing.Queue,
    message_queue_for_buttons: multiprocessing.Queue,
    message_queue_for_watch: multiprocessing.Queue,
):
    watch_setup = False
    current_datetime = None
    current_changing = "minutes"
    automatic_watch_setup = False

    while True:
        if not message_queue_in.empty():
            recieved_message = message_queue_in.get()
            if recieved_message == "Watch setup started!":
                automatic_watch_setup = True
            elif recieved_message == "Watch setup is done!":
                automatic_watch_setup = False

        if not automatic_watch_setup:
            if start_watch_setup(
                switch=WATCH_SETUP_SWITCH, watch_setup_state=watch_setup
            ):
                watch_setup = True
                message_queue_for_display.put("Manual watch setup started.")
                message_queue_for_buttons.put("Manual watch setup started.")
                message_queue_for_watch.put("Manual watch setup started.")
            elif not is_pressed(button=WATCH_SETUP_SWITCH):
                if watch_setup == True:
                    log_last_watch_time(date_time=current_datetime.replace(second=0))
                    current_datetime = None
                    watch_setup = False
                    current_changing = "minutes"
                    clear()
                    message_queue_for_display.put("Manual watch setup done.")
                    message_queue_for_buttons.put("Manual watch setup done.")
                    message_queue_for_watch.put("Manual watch setup done.")

            if watch_setup:
                if current_datetime == None:
                    current_datetime = datetime.datetime.now()
                    clear()
                    write(1, 0, "Na satu: " + current_datetime.strftime("%H:%M"))
                    write(13, 1, "**")

                if is_pressed(LEFT_BUTTON):
                    current_changing = "hours"
                    clear()
                    write(1, 0, "Na satu: " + current_datetime.strftime("%H:%M"))
                    write(10, 1, "**")
                if is_pressed(RIGHT_BUTTON):
                    current_changing = "minutes"
                    clear()
                    write(1, 0, "Na satu: " + current_datetime.strftime("%H:%M"))
                    write(13, 1, "**")
                if is_pressed(UP_BUTTON):
                    if current_changing == "minutes":
                        current_datetime = current_datetime + datetime.timedelta(
                            minutes=1
                        )
                        write(1, 0, "Na satu: " + current_datetime.strftime("%H:%M"))
                    elif current_changing == "hours":
                        current_datetime = current_datetime + datetime.timedelta(
                            hours=1
                        )
                        write(1, 0, "Na satu: " + current_datetime.strftime("%H:%M"))
                if is_pressed(DOWN_BUTTON):
                    if current_changing == "minutes":
                        current_datetime = current_datetime - datetime.timedelta(
                            minutes=1
                        )
                        write(1, 0, "Na satu: " + current_datetime.strftime("%H:%M"))
                    elif current_changing == "hours":
                        current_datetime = current_datetime - datetime.timedelta(
                            hours=1
                        )
                        write(1, 0, "Na satu: " + current_datetime.strftime("%H:%M"))
                if is_pressed(F0_BUTTON):
                    GPIO.output(HOUR_HANDLE, GPIO.HIGH)
                    GPIO.output(F0_LED, GPIO.HIGH)
                if not is_pressed(F0_BUTTON):
                    GPIO.output(HOUR_HANDLE, GPIO.LOW)
                    GPIO.output(F0_LED, GPIO.LOW)
                if is_pressed(F1_BUTTON):
                    GPIO.output(MINUTE_HANDLE, GPIO.HIGH)
                    GPIO.output(F1_LED, GPIO.HIGH)
                if not is_pressed(F1_BUTTON):
                    GPIO.output(MINUTE_HANDLE, GPIO.LOW)
                    GPIO.output(F1_LED, GPIO.LOW)

        # Debounce delay.
        time.sleep(0.1)
