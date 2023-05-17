"""This is main belfry module.

**************************************
Author name  : Igor
authors email: igor.radic3vu@gmail.com
**************************************

** PINS:  
 
F1_AND_CANCEL_BUTTON = 16 
F2_AND_ENTER_BUTTON = 20

F1_LED = 18
F2_LED = 21

UP_BUTTON = 17
RIGHT_BUTTON = 27 
DOWN_BUTTON = 22
LEFT_BUTTON = 5

BELL_A = 26
BELL_B = 19
BELL_C = 13
BELL_D = 6

MINUTE_HANDLE = 23
HOUR_HANDLE = 24

WATCH_SETUP_LOCK = 12
"""

from watch import watch
from display import display
from lcd1602 import init, write, clear
import multiprocessing
import time

# Display init.
init(0x27, 1)  # 27 is I2C address of display, 1 is backlight ON


def show_initial_message():
    """
    This function shows initial message on startup.
    """
    write(0, 0, "Hvaljen Isus i")
    write(0, 1, "Marija!")
    time.sleep(2)
    clear()


def main():
    # First show initial message.
    show_initial_message()

    # Queue for sending current time every second from watch to display and bells module.
    current_datetime_queue = multiprocessing.Queue()

    # Queue for communication between processes.
    message_queue = multiprocessing.Queue()

    # Starting watch process.
    multiprocessing.Process(
        target=watch, args=(current_datetime_queue, message_queue)
    ).start()

    # Starting display process.
    multiprocessing.Process(
        target=display, args=(current_datetime_queue, message_queue)
    ).start()


if __name__ == "__main__":
    main()
