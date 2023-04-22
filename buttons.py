import time
import RPi.GPIO as GPIO
from multiprocessing import Queue

# use Raspberry Pi 4B board pin numbers
GPIO.setmode(GPIO.BCM)

# TODO Remove wire colors
# Set GPIO pins
F1_BUTTON = 4  # zelena
F2_BUTTON = 17  # ljubicasta
F3_BUTTON = 27  # plava
F4_BUTTON = 22  # bijela

F1_LED = 18
F2_LED = 25
F3_LED = 12
F4_LED = 5

buttons = [F1_BUTTON, F2_BUTTON, F3_BUTTON, F4_BUTTON]
leds = [F1_LED, F2_LED, F3_LED, F4_LED]

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


def buttons_main(states_queue: Queue):
    """This is main function for buttons.

    It checks button states and change program states if needed.
    On program states change, it sends new program states to other functions.
    """
    # Declare initial states
    buttons_state = [False, False, False, False]
    program_states = [False, False, False, False]

    while True:
        # Get current buttons states
        for i, button, state in zip(range(len(buttons)), buttons, buttons_state):
            buttons_state[i] = is_pressed(button=button, previous_pressed=state)
            if buttons_state[i]:
                # Change current program state
                program_states[i] = not program_states[i]
                # Send new program states to other processes
                states_queue.put(program_states)

        # Debounce delay
        time.sleep(0.1)

        # Set LEDs states based on program states
        for led, state in zip(leds, program_states):
            if state:
                GPIO.output(led, GPIO.HIGH)
            else:
                GPIO.output(led, GPIO.LOW)
