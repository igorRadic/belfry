"""This is main belfry module.

**************************************
Author name  : Igor
authors email: igor.radic3vu@gmail.com
**************************************

** OUTPUT PINS:  

BELL_A = 6
BELL_B = 13
BELL_C = 19
BELL_D = 26

MINUTE_HANDLE = 23
HOUR_HANDLE = 24

16x2_DISPLAY = SDA1, SCL1, 5V, GND 

F0_LED = 18
F1_LED = 21

** INPUT PINS: 

F0_BUTTON = 16
F1_BUTTON = 20

UP_BUTTON = 17
RIGHT_BUTTON = 5
DOWN_BUTTON = 22
LEFT_BUTTON = 27

WATCH_SETUP_SWITCH = 12

FREE GPIO PINS: 4, 25 
"""

import multiprocessing
import time

from bells import bells
from display import display
from function_buttons import function_buttons
from lcd1602 import clear, init, write
from manual_watch_setup import manual_watch_setup
from watch import watch

# Display init.
init(0x27, 1)  # 27 is I2C address of display, 1 is backlight ON


def show_initial_message() -> None:
    """
    This function shows initial message on startup.
    """
    write(0, 0, "Hvaljen Isus i")
    write(0, 1, "Marija!")
    time.sleep(2)
    clear()


def main() -> None:
    # First show initial message.
    show_initial_message()

    # Queues for communication between processes.
    message_queue_for_display = multiprocessing.Queue()
    states_queue_for_bells = multiprocessing.Queue()

    # Queue for sending current datetime to display module.
    current_datetime_for_display = multiprocessing.Queue()

    # Queue for sending current datetime to bells module.
    current_datetime_for_bells = multiprocessing.Queue()

    # Queue for sending current datetime to buttons module.
    current_datetime_for_buttons = multiprocessing.Queue()

    # Manual watch setup queues.
    message_queue_for_buttons = multiprocessing.Queue()
    message_queue_for_watch = multiprocessing.Queue()

    message_queue_for_manual_watch_setup = multiprocessing.Queue()

    # Starting display process.
    multiprocessing.Process(
        target=display,
        args=(current_datetime_for_display, message_queue_for_display),
    ).start()

    # Start function buttons process.
    multiprocessing.Process(
        target=function_buttons,
        args=(
            states_queue_for_bells,
            current_datetime_for_buttons,
            message_queue_for_buttons,
        ),
    ).start()

    # Start bells process.
    multiprocessing.Process(
        target=bells,
        args=(
            current_datetime_for_bells,
            states_queue_for_bells,
            message_queue_for_display,
        ),
    ).start()

    # Starting watch process.
    multiprocessing.Process(
        target=watch,
        args=(
            current_datetime_for_display,
            current_datetime_for_bells,
            current_datetime_for_buttons,
            message_queue_for_display,
            message_queue_for_watch,
            message_queue_for_manual_watch_setup,
        ),
    ).start()

    multiprocessing.Process(
        target=manual_watch_setup,
        args=(
            message_queue_for_manual_watch_setup,
            message_queue_for_display,
            message_queue_for_buttons,
            message_queue_for_watch,
        ),
    ).start()


if __name__ == "__main__":
    main()
