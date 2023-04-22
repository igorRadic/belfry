"""Module for displaying informations on 16x2 display.

It displays current date and time and it is used for
watch setup.
"""

from multiprocessing import Queue


def display(message_queue: Queue):
    """This is main display function

    It displays messages from message queue."""

    while True:
        if message_queue.empty():
            continue
        else:
            recieved_message = message_queue.get()
        print(recieved_message)
