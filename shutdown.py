
import RPi.GPIO as GPIO
import subprocess
import time

SHUTDOWN  = 15
def check_shutdown_setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(SHUTDOWN , GPIO.IN, pull_up_down=GPIO.PUD_UP)
def check_shutdown():
    if GPIO.input(SHUTDOWN) == 0:
        GPIO.cleanup()
        cmd = "sudo shutdown -h now"
        subprocess.call(cmd, shell=True)
        return False
    return True
            
if __name__ == '__main__':
    check_shutdown_setup()
    while check_shutdown():
        time.sleep(.05)