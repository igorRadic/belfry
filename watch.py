"""Module for watch manipulation.

The watch has only hour and minute handle,
this module manipulates the GPIO pins which then
manipulate relays that turn on and off
electric motors on which are handles.
There are two GPIO pins, each for one handle, 
according to that there are two electric motors.
"""

import datetime
import multiprocessing
from time import perf_counter

import RPi.GPIO as GPIO

from utils import delay

# Use Raspberry Pi 4B board pin numbers.
GPIO.setmode(GPIO.BCM)

# Ignore GPIO warnings.
GPIO.setwarnings(False)

# Set GPIO pins for watch handles.
MINUTE_HANDLE = 23
HOUR_HANDLE = 24

# set up GPIO pin modes
for pin in [MINUTE_HANDLE, HOUR_HANDLE]:
    GPIO.setup(pin, GPIO.OUT)

# Declare how long to move each handle
# and when to start moving handles.
MINUTE_HANDLE_DELAY = 3.1  # [s]
HOUR_HANDLE_DELAY = 3.1  # [s]

MINUTE_HANDLE_START = 57  # [s]
HOUR_HANDLE_START = 2  # [s]

ONE_SECOND = 1


def log_minute_handle_move() -> None:
    """
    Log that minute handle has moved.
    """
    with open("handles_movement_log.txt", "w") as txt_file:
        txt_file.write("minute_handle")


def log_hour_handle_move() -> None:
    """
    Log that hour handle has moved.
    """
    with open("handles_movement_log.txt", "w") as txt_file:
        txt_file.write("hour_handle")


def move_minute_handle() -> None:
    """
    This function sets GPIO pin to HIGH which turns on electric motor.
    Minute handle moves as long as the GPIO pin is in HIGH state.
    """
    print("-=--=- start moving: Minute handle  -=--=-")
    GPIO.output(MINUTE_HANDLE, GPIO.HIGH)
    delay(seconds=MINUTE_HANDLE_DELAY)
    GPIO.output(MINUTE_HANDLE, GPIO.LOW)
    print("-=--=- stop moving: Minute handle  -=--=-")
    log_minute_handle_move()


def move_hour_handle() -> None:
    """
    This function sets GPIO pin to HIGH which turns on electric motor.
    Hour handle moves as long as the GPIO pin is in HIGH state.
    """
    print("-=- start moving: Hour handle -=-")
    GPIO.output(HOUR_HANDLE, GPIO.HIGH)
    delay(HOUR_HANDLE_DELAY)
    GPIO.output(HOUR_HANDLE, GPIO.LOW)
    print("-=- stop moving: Hour handle  -=-")
    log_hour_handle_move()


def log_last_watch_time(date_time: datetime.datetime) -> None:
    """
    Log recieved time to text file.
    """
    with open("watch_time.txt", "w") as txt_file:
        txt_file.write(f"{date_time.strftime('%H:%M:%S')}")


def get_last_watch_time() -> datetime.datetime:
    """
    Get last watch time from text file.
    """
    with open("watch_time.txt", "r") as txt_file:
        last_watch_time = (
            datetime.datetime.strptime(txt_file.readline(), "%H:%M:%S")
            .time()
            .replace(second=0)
        )
    return last_watch_time


def handles_synchronized() -> bool:
    """
    This function checks the last movement of handles and returns True
    if handles are synchronized and False if not.

    Handle are not synchronized if some problem occurred that caused
    the program to stop after moving the minute handle and
    before moving hour handle.
    In this case the hour handle did not move and now must move
    so the handles stay synchronized.
    """
    try:
        with open("handles_movement_log.txt", "r") as txt_file:
            last_movement = txt_file.readline()
        if last_movement == "hour_handle":
            return True
        elif last_movement == "minute_handle":
            return False
        else:
            return True
    except FileNotFoundError:
        return True


def minute_handle_last_moved() -> bool:
    """
    This function checks if minute handle last moved.
    """
    try:
        with open("handles_movement_log.txt", "r") as txt_file:
            last_movement = txt_file.readline()
        if last_movement == "minute_handle":
            return True
        else:
            return False
    except FileNotFoundError:
        return True


def watch_setup(
    minutes: int,
    last_watch_datetime: datetime.datetime,
    watch_setup_queue: multiprocessing.Queue,
) -> None:
    """
    This function is called when there is difference between current and
    watch time, this function calls moving hour and minute handles as many
    times as the watch is late (in minutes).
    """
    iterations = 0

    # First check if handles moved identically in last handle movement.
    if not handles_synchronized():
        # If they not, move hour handle to synchronize them.
        print("Hour handle has not moved last time!")
        print(f"      # 0. watch setup iteration (only hour handle moves).")
        move_hour_handle()
        log_last_watch_time(
            date_time=last_watch_datetime.replace(second=0)
            + datetime.timedelta(minutes=1)
        )
        minutes = minutes - 1
        if minutes == 0:
            print("   ** Watch setup is done. **")
            watch_setup_queue.put("Watch setup is done!")
            return

    # If difference is more than 12 hours, substract 12 hours.
    if minutes > 720:  # 12 * 60 minutes = 720 minutes
        iterations = minutes - 720
    else:
        iterations = minutes

    print(f"--- Required {iterations} iterations. ---")

    for iteration in range(iterations):
        print(f"      # {iteration + 1}. watch setup iteration.")

        # Move minute handle.
        minute_handle_process = multiprocessing.Process(target=move_minute_handle)
        minute_handle_process.start()
        minute_handle_process.join()

        # Move hour handle.
        hour_handle_process = multiprocessing.Process(target=move_hour_handle)
        hour_handle_process.start()
        hour_handle_process.join()

        # Log new watch time.
        log_last_watch_time(
            date_time=last_watch_datetime.replace(second=0)
            + datetime.timedelta(minutes=iteration + 1)
        )

    print("   ** Watch setup is done. **")
    watch_setup_queue.put("Watch setup is done!")


def wait_until_next_second(counter_from_which_it_is_waiting: float) -> None:
    """
    Wait one second from retrieved perf counter state.
    """
    execution_time = perf_counter() - counter_from_which_it_is_waiting
    if execution_time < ONE_SECOND:
        while perf_counter() < counter_from_which_it_is_waiting + ONE_SECOND:
            pass


def watch(
    current_datetime_for_display: multiprocessing.Queue,
    current_datetime_for_bells: multiprocessing.Queue,
    current_datetime_for_buttons: multiprocessing.Queue,
    message_queue_for_display: multiprocessing.Queue,
    message_queue_in: multiprocessing.Queue,
    message_queue_for_manual_watch_setup: multiprocessing.Queue,
) -> None:
    """This function is main watch function.

    It sends tick to other processes every second and
    it starts moving handles when it is time for it.
    Also it checks if watch time is correct, if not
    calls watch setup.
    """
    # Flag which indicates that watch is current in setup mode.
    watch_is_setting = False
    # Queue for communication with watch setup process.
    watch_setup_queue = multiprocessing.Queue()
    # Flag which indicates that app is on startup.
    app_on_startup = True
    # Flag which indicates that minute handle has moved in previous iteration.
    minute_handle_moved = True
    """
    When watch setup ends after minute handle movement and before 
    hour handle movement, hour handle moves but minute handle did not move,
    this flag is used to track this.
    """

    while True:
        # Get current perf counter state, date and time.
        loop_start_time = perf_counter()
        current_datetime = datetime.datetime.now()

        # Send tick to other processes.
        current_datetime_message = current_datetime.strftime("%d/%m/%y %H:%M:%S")
        current_datetime_for_display.put(current_datetime_message)
        current_datetime_for_bells.put(current_datetime_message)
        current_datetime_for_buttons.put(current_datetime_message)

        if not message_queue_in.empty():
            recieved_message = message_queue_in.get()
            if recieved_message == "Manual watch setup started.":
                watch_is_setting = True
            elif recieved_message == "Manual watch setup done.":
                watch_is_setting = False

        if watch_is_setting:
            if watch_setup_queue.empty():
                # Wait and go to next loop iteration if watch is in setup mode.
                wait_until_next_second(counter_from_which_it_is_waiting=loop_start_time)
                continue
            else:
                recieved_message = watch_setup_queue.get()
                if recieved_message == "Watch setup is done!":
                    # Continue with normal work, go further in this loop.
                    watch_is_setting = False
                    app_on_startup = False
                    message_queue_for_display.put("Watch setup is done!")
                    message_queue_for_manual_watch_setup.put("Watch setup is done!")

        # Get last watch time.
        last_watch_time = get_last_watch_time()

        # Convert it to datetime so that current datetime and last watch time can be compared.
        last_watch_time = datetime.datetime.combine(
            current_datetime.date(), last_watch_time
        )

        # Calculate the time difference.
        if current_datetime < last_watch_time:
            # If current_datetime is earlier in the day, assume that last_watch_time is from yesterday.
            last_watch_time = datetime.datetime.combine(
                current_datetime.date() - datetime.timedelta(days=1),
                last_watch_time.time(),
            )
        time_delta = current_datetime - last_watch_time

        # Convert time difference to minutes.
        time_delta = int(time_delta.total_seconds() / 60)

        if app_on_startup and time_delta > 0:
            watch_is_setting = True
            multiprocessing.Process(
                target=watch_setup,
                args=(time_delta, last_watch_time, watch_setup_queue),
            ).start()
            message_queue_for_display.put("Watch setup started!")
            message_queue_for_manual_watch_setup.put("Watch setup started!")
            wait_until_next_second(counter_from_which_it_is_waiting=loop_start_time)
            continue

        # If there is time delta go to watch setup mode,
        # ignore time delta if watch handles are moving right now in normal mode.
        if (
            time_delta > 0
            and current_datetime.second > HOUR_HANDLE_START + HOUR_HANDLE_DELAY + 1
            and current_datetime.second < MINUTE_HANDLE_START - 1
        ):
            print(f"Current watch time is: {last_watch_time.strftime('%H:%M:%S')}")
            print(f"Current time is: {current_datetime.strftime('%H:%M:%S')}")
            print(
                f"Difference between curret time and watch time is {time_delta} minutes!"
            )
            print("   ** Turning to watch setup mode. **")
            watch_is_setting = True
            multiprocessing.Process(
                target=watch_setup,
                args=(time_delta, last_watch_time, watch_setup_queue),
            ).start()
            message_queue_for_display.put("Watch setup started!")
            message_queue_for_manual_watch_setup.put("Watch setup started!")
            wait_until_next_second(counter_from_which_it_is_waiting=loop_start_time)
            continue

        # Check if is it time for minute handle moving, if it is, move minute handle.
        if int(current_datetime.strftime("%S")) == MINUTE_HANDLE_START:
            minute_handle_process = multiprocessing.Process(target=move_minute_handle)
            minute_handle_process.start()

        # Check if is it time for hour handle moving, if it is, move hour handle.
        if int(current_datetime.strftime("%S")) == HOUR_HANDLE_START:
            if not minute_handle_last_moved():
                minute_handle_moved = False
            hour_handle_process = multiprocessing.Process(target=move_hour_handle)
            hour_handle_process.start()
            log_last_watch_time(
                date_time=last_watch_time.replace(second=0)
                + datetime.timedelta(minutes=1)
            )

        if (
            not minute_handle_moved
            and int(current_datetime.strftime("%S"))
            > HOUR_HANDLE_START + HOUR_HANDLE_DELAY + 1
            and int(current_datetime.strftime("%S"))
            < MINUTE_HANDLE_START - MINUTE_HANDLE_DELAY - 1
        ):
            # If hour handle moved but minute handle did not move, move minute handle
            # after the hour handle has has moved.
            minute_handle_process = multiprocessing.Process(target=move_minute_handle)
            minute_handle_process.start()
            minute_handle_moved = True
            # Override minute handle move log with hour handle move log so the algorithm
            # won't assume that handles are not synchronized.
            log_hour_handle_move()

        wait_until_next_second(counter_from_which_it_is_waiting=loop_start_time)
