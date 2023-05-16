"""This is main belfry module.

**************************************
Author name  : Igor
authors email: igor.radic3vu@gmail.com
**************************************

** PINS:  
 
F1_AND_CANCEL_BUTTON = 16 
F2_AND_ENTER_BUTTON = 20

F1_LED = 18
F2_LED = 25

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

SLobodni: 
16, 20, 21
"""

from watch import watch
from display import display
import multiprocessing


def main():
    message_queue = multiprocessing.Queue()
    watch_process = multiprocessing.Process(target=watch, args=(message_queue,)).start()
    display_process = multiprocessing.Process(
        target=display, args=(message_queue,)
    ).start()


if __name__ == "__main__":
    main()
