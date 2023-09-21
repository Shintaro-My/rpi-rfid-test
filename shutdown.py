
import RPi.GPIO as GPIO
import subprocess
import time

SHUTDOWN  = 15
REBOOT    = 16
def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(SHUTDOWN , GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(REBOOT   , GPIO.IN, pull_up_down=GPIO.PUD_UP)
def check():
    if GPIO.input(SHUTDOWN) == 0:
        GPIO.cleanup()
        cmd = "sudo shutdown -h now"
        subprocess.call(cmd, shell=True)
        return False
    elif GPIO.input(REBOOT) == 0:
        GPIO.cleanup()
        cmd = "sudo reboot"
        subprocess.call(cmd, shell=True)
        return False
    return True
            
if __name__ == '__main__':
    setup()
    print('enbale gpio-shutdown/reboot: (15, 16)')
    while check():
        time.sleep(.05)