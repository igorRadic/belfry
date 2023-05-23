# Belfry controller 🏫

This package controlls four bells and clock on belfry. Bells and clock handles are moved by electric motors and they are controlled by relays. 

It runs on Raspberry Pi 4 Model B. 🚀

## Features:
- Automatic clock setup
- Manual clock setup
- Automatic ringing
- Manual ringing
- Two function buttons which can engade two ringing modes
- Display which shows current date and time

## Wiring diagram:
![wiring diagram](images/wiring_diagram.png)

## Setup:

Before running this package add three txt files:
`watch_time.txt`, `handles_movement_log.txt` and `function_buttons.txt`, they are logs that help preserve the data necessary for work and to keep the correct time on the belfry clock. 

In `watch_time.txt` add current time on belfry clock. Like this: 
```
17:24:00
```

`handles_movement_log.txt` tracks which clock handle last moved, add in this file next line:
```
hour_handle
```

and finnaly add next lines in `function_buttons.txt` file:
```
True 23/05/23 15:25:11 
True 23/05/23 15:25:10 

```
in this way it is tracked which (ringing) function is activated and when.

Also you can enable executing `main.py` file on Raspberry Pi startup, you can see how to do that [here](https://people.utm.my/shaharil/run-programs-on-your-raspberry-pi-at-startup/).