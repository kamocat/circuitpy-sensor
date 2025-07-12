import microcontroller as uc
import adafruit_logging
import storage
import supervisor

print("SW:0.2.0")

storage.remount("/", readonly=False) #Make flash read/write
log = adafruit_logging.getLogger("errors")
try:
    log.addHandler(adafruit_logging.RotatingFileHandler("/errors.log", maxBytes=65536, backupCount=32))
    log.addHandler(adafruit_logging.StreamHandler())
    print("Logging to file")
except Exception as e:
    print(f"Not logging to file due to {e}")
e = supervisor.get_previous_traceback()
if e is not None:
    log.critical(e)
log.warning(f"Reset from {uc.cpu.reset_reason}")
