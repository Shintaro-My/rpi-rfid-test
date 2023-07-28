import time
import RPi.GPIO as GPIO
import questionary as qy

DB_NAME = 'user.db'

BZ_INTERVAL = 0.075

BZ        = 11
RELAY     = 15
LED_GREEN = 36
LED_RED   = 37

def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(BZ       , GPIO.OUT)
    GPIO.setup(RELAY    , GPIO.OUT)
    GPIO.setup(LED_GREEN, GPIO.OUT)
    GPIO.setup(LED_RED  , GPIO.OUT)

def relay(bln):
    GPIO.output(RELAY    , bln)

def led_all_off():
    GPIO.output(LED_GREEN, False)
    GPIO.output(LED_RED  , False)
def led_green():
    GPIO.output(LED_GREEN, True )
    GPIO.output(LED_RED  , False)
def led_red():
    GPIO.output(LED_GREEN, False)
    GPIO.output(LED_RED  , True )
    

def buzzer(n = 1, fn1=lambda:1, fn2=lambda:1):
    for i in range(n):
        if i: time.sleep(BZ_INTERVAL)
        GPIO.output(BZ, True )
        fn1()
        time.sleep(BZ_INTERVAL)
        GPIO.output(BZ, False)
        fn2()


def init_db(conn, cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Users(
            UserId    TEXT PRIMARY KEY,
            UserName  TEXT NOT NULL,
            Note      TEXT,
            CreatedAt DATETIME NOT NULL,
            LastSeen  DATETIME
        )
        """.strip()
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Anonymous(
            UserId     TEXT PRIMARY KEY,
            LastUpdate DATETIME NOT NULL
        )
        """.strip()
    )
    conn.commit()
    
    

def confirm(txt):
    return qy.select(txt, choices=[
        qy.Choice(title='No', value=False),
        qy.Choice(title='Yes', value=True)
    ]).ask()