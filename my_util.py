import time
import RPi.GPIO as GPIO

BZ_INTERVAL = 0.075

BZ        = 11
LED_GREEN = 36
LED_RED   = 37

def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(BZ       , GPIO.OUT)
    GPIO.setup(LED_GREEN, GPIO.OUT)
    GPIO.setup(LED_RED  , GPIO.OUT)
    

def led_green():
    GPIO.output(LED_GREEN, True )
    GPIO.output(LED_RED  , False)
def led_red():
    GPIO.output(LED_GREEN, False)
    GPIO.output(LED_RED  , True )
    

def buzzer(n = 1):
    for i in range(n):
        if i: time.sleep(BZ_INTERVAL)
        GPIO.output(BZ, True )
        time.sleep(BZ_INTERVAL)
        GPIO.output(BZ, False)


def init_db(conn, cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Users(
            UserId   TEXT PRIMARY KEY,
            UserName TEXT NOT NULL,
            Note     TEXT
        )
        """.strip()
    )
    conn.commit()