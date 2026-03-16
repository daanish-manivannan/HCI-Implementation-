import threading
import time
import settings_gui

print("Main thread starting")
settings_gui.launch_dashboard()

try:
    while True:
        time.sleep(1)
        print("Main thread running...")
except KeyboardInterrupt:
    print("Exiting")
