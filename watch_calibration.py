"""Watch calibration module.

This module is used to move watch handles 60 times, it is used
to see if watch handles actually moved for 60 minutes.
"""

import multiprocessing

from watch import move_hour_handle, move_minute_handle


print("Watch calibration started.")

for iteration in range(60):
    print(f"{iteration + 1} iteration.")

    # Move minute handle.
    minute_handle_process = multiprocessing.Process(target=move_minute_handle)
    minute_handle_process.start()
    minute_handle_process.join()

    # Move hour handle.
    hour_handle_process = multiprocessing.Process(target=move_hour_handle)
    hour_handle_process.start()
    hour_handle_process.join()

print("Watch calibration ended.")
