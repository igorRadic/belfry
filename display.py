"""Module for displaying informations on 16x2 display.

It displays current date and time and it is used for
watch setup.
"""

from multiprocessing import Queue
from lcd1602 import write, clear


def display(current_datetime_queue: Queue, message_queue: Queue):
    """This is main display function

    It displays messages from message queue."""

    show_datetime = True

    while True:
        if not message_queue.empty():
            recieved_message = message_queue.get()
            if recieved_message == "Watch setup started!":
                write(0, 0, "Pricekajte, sat")
                write(0, 1, "se namjesta!")
                show_datetime = False
            elif recieved_message == "Watch setup is done!":
                show_datetime = True
                clear()

        elif not current_datetime_queue.empty():
            current_date_and_time = current_datetime_queue.get()
            print(current_date_and_time)
            if show_datetime:
                write(0, 0, current_date_and_time[0:8])
                write(0, 1, current_date_and_time[9:17])
        else:
            continue
