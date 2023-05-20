"""Module for displaying informations on 16x2 display.

It displays current date and time, watch setup informations and
ringing informations.
"""

import multiprocessing

from lcd1602 import clear, write


def display(
    current_datetime_queue: multiprocessing.Queue, message_queue: multiprocessing.Queue
) -> None:
    """This is main display function.

    It displays messages from current_datetime_queue and message_queue.
    """
    # Flags which indicates which information to show on display.
    show_watch_setup = False
    show_ringing = False

    while True:
        if not message_queue.empty():
            recieved_message = message_queue.get()
            if recieved_message == "Watch setup started!":
                if not show_ringing:
                    write(0, 0, "Pricekajte, sat")
                    write(0, 1, "se namjesta!")
                show_watch_setup = True
            elif recieved_message == "Watch setup is done!":
                show_watch_setup = False
                if not show_ringing:
                    clear()
            elif "Ringing" in recieved_message:
                show_ringing = True
                clear()
                # In the first line show ringing name.
                write(0, 0, recieved_message[8:24])
                # In the second line show which bells are ringing.
                write(0, 1, recieved_message[25:])
            elif "Stop ringing" in recieved_message:
                show_ringing = False
                if not show_watch_setup:
                    clear()

        elif not current_datetime_queue.empty():
            current_date_and_time = current_datetime_queue.get()
            if not show_watch_setup and not show_ringing:
                # In the first line show current date.
                write(0, 0, current_date_and_time[0:8])
                # In the second line show current time.
                write(0, 1, current_date_and_time[9:17])

        else:
            continue
