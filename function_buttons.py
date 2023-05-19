import time
import RPi.GPIO as GPIO
from multiprocessing import Queue
import datetime

# use Raspberry Pi 4B board pin numbers
GPIO.setmode(GPIO.BCM)

# Set GPIO pins
# UP_BUTTON = 17
# RIGHT_BUTTON = 27
# DOWN_BUTTON = 22
# LEFT_BUTTON = 5

S1_BUTTON = 16
S3_BUTTON = 20

S1_LED = 18
S3_LED = 21

buttons = [S1_BUTTON, S3_BUTTON]
leds = [S1_LED, S3_LED]

# set up GPIO pin modes
for pin in buttons:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for pin in leds:
    GPIO.setup(pin, GPIO.OUT)


def is_pressed(previous_pressed: bool, button: int) -> bool:
    """This function checks if button is pressed.

    Note: Button is pressed when input pin is LOW and
    button previously was not pressed.
    """
    if not GPIO.input(button):
        if previous_pressed == False:
            return True
    else:
        return False


def log_function_buttons_states(
    function_buttons_states: list[bool], current_datetime: datetime.datetime
):
    """
    Log function buttons states change in text file.
    """
    old_states, old_states_datetime = get_function_buttons_states()
    with open("function_buttons.txt", "w") as txt_file:
        for state, old_state, old_datetime in zip(
            function_buttons_states, old_states, old_states_datetime
        ):
            if state != old_state:
                txt_file.writelines(
                    f"{state} {current_datetime.strftime('%d/%m/%y %H:%M:%S')} \n"
                )
            else:
                txt_file.writelines(
                    f"{old_state} {old_datetime.strftime('%d/%m/%y %H:%M:%S')} \n"
                )


def get_function_buttons_states():
    """
    Get last function buttons states from text file.
    """
    states = []
    states_datetime = []
    with open("function_buttons.txt", "r") as txt_file:
        lines = txt_file.readlines()
        for line in lines:
            [state, state_date, state_time, _] = line.split(" ")
            state_datetime_string = state_date + " " + state_time
            state_datetime = datetime.datetime.strptime(
                state_datetime_string, "%d/%m/%y %H:%M:%S"
            )
            if state == "True":
                states.append(True)
            else:
                states.append(False)
            states_datetime.append(state_datetime)
    return states, states_datetime


def function_buttons(states_queue: Queue, current_datetime_queue: Queue):
    """This is main function for buttons.

    It checks button states and change program states if needed.
    On program states change, it sends new program states to other functions.
    """
    # Declare initial states.
    buttons_state = [False, False]
    program_states = [False, False]

    # Set funciton elapse datetime.
    states_datetime = [
        datetime.datetime.now().replace(hour=13, minute=0, second=0),
        datetime.datetime.now().replace(hour=15, minute=0, second=0),
    ]

    for i in range(len(states_datetime)):
        if datetime.datetime.now() > states_datetime[i]:
            states_datetime[i] = states_datetime[i] + datetime.timedelta(days=1)

    # Check for logged program states.
    logged_states, logged_states_datetime = get_function_buttons_states()

    # Set current program states to logged program states.
    for i in range(len(program_states)):
        # Update program state only if logged state not expired.
        delta = states_datetime[i] - logged_states_datetime[i]
        if int(delta.total_seconds() / (60 * 60)) < 24:
            program_states[i] = logged_states[i]

    while True:
        # Get current buttons states.
        for i, button, state in zip(range(len(buttons)), buttons, buttons_state):
            buttons_state[i] = is_pressed(button=button, previous_pressed=state)
            if buttons_state[i]:
                # Change current program state.
                program_states[i] = not program_states[i]
                # Send new program states to other processes.
                states_queue.put(program_states)
                log_function_buttons_states(
                    current_datetime=datetime.datetime.now(),
                    function_buttons_states=program_states,
                )

        # Debounce delay.
        time.sleep(0.1)

        if not current_datetime_queue.empty():
            recieved_message = current_datetime_queue.get()

            # Convert str to datetime.
            current_datetime = datetime.datetime.strptime(
                recieved_message, "%d/%m/%y %H:%M:%S"
            )

            if (
                program_states[0]
                and current_datetime.hour == 13
                and current_datetime.minute == 0
                and current_datetime.second == 0
            ):
                # Change current program state.
                program_states[0] = False
                # Send new program states to other processes.
                states_queue.put(program_states)
                log_function_buttons_states(
                    current_datetime=datetime.datetime.now(),
                    function_buttons_states=program_states,
                )
            elif (
                program_states[1]
                and current_datetime.hour == 15
                and current_datetime.minute == 0
                and current_datetime.second == 0
            ):
                # Change current program state.
                program_states[1] = False
                # Send new program states to other processes.
                states_queue.put(program_states)
                log_function_buttons_states(
                    current_datetime=datetime.datetime.now(),
                    function_buttons_states=program_states,
                )

        # Set LEDs states based on program states.
        for led, state in zip(leds, program_states):
            if state:
                GPIO.output(led, GPIO.HIGH)
            else:
                GPIO.output(led, GPIO.LOW)
