"""This is main belfry module.

**************************************
Author name  : Igor
authors email: igor.radic3vu@gmail.com
**************************************

** PINS:  
 
F1_BUTTON = 4
F2_BUTTON = 17
F3_BUTTON = 27
F4_BUTTON = 22

F1_LED = 18
F2_LED = 25
F3_LED = 12
F4_LED = 5

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
