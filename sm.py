import microcontroller


# Enter safe mode
def enter():
    microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
    microcontroller.reset()


# Exit safe mode
def exit():
    microcontroller.reset()
