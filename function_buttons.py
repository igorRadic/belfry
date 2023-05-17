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


def function_buttons(states_queue: Queue, current_datetime_queue: Queue):
    """This is main function for buttons.

    It checks button states and change program states if needed.
    On program states change, it sends new program states to other functions.
    """
    # Declare initial states.
    buttons_state = [False, False]
    program_states = [False, False]

    while True:
        # Get current buttons states.
        for i, button, state in zip(range(len(buttons)), buttons, buttons_state):
            buttons_state[i] = is_pressed(button=button, previous_pressed=state)
            if buttons_state[i]:
                # Change current program state.
                program_states[i] = not program_states[i]
                # Send new program states to other processes.
                states_queue.put(program_states)

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

        # Set LEDs states based on program states.
        for led, state in zip(leds, program_states):
            if state:
                GPIO.output(led, GPIO.HIGH)
            else:
                GPIO.output(led, GPIO.LOW)
