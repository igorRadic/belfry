"""Module for displaying informations on 16x2 display.

It displays current date and time and it is used for
watch setup.
"""

from multiprocessing import Queue
from lcd1602 import init, write


def display(message_queue: Queue):
    """This is main display function

    It displays messages from message queue."""

    init(0x27, 1) # 27 is I2C address of display, 1 is backlight ON

    while True:
        if message_queue.empty():
            continue
        else:
            recieved_message = message_queue.get()
        print(recieved_message)
        write(0, 0, recieved_message)
        write(0, 1, 'string')

