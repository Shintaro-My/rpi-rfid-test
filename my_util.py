import time
import RPi.GPIO as GPIO
import traceback
import questionary as qy

DB_NAME = 'user.db'

BZ_INTERVAL = 0.075

BZ        = 11
RELAY     = 22
LED_GREEN = 36
LED_RED   = 37

LEAD_SW   = 33


def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(BZ       , GPIO.OUT)
    GPIO.setup(RELAY    , GPIO.OUT)
    GPIO.setup(LED_GREEN, GPIO.OUT)
    GPIO.setup(LED_RED  , GPIO.OUT)
    GPIO.setup(LEAD_SW  , GPIO.IN, pull_up_down=GPIO.PUD_UP)

def relay(bln):
    GPIO.output(RELAY    , bln)

def led_all_off():
    GPIO.output(LED_GREEN, False)
    GPIO.output(LED_RED  , False)
def led_all_on():
    GPIO.output(LED_GREEN, True )
    GPIO.output(LED_RED  , True )
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

def is_door_open():
    return GPIO.input(LEAD_SW) == 1

def init_db(conn, cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Config(
            Attribute TEXT PRIMARY KEY,
            Status    INTEGER,
            Note      TEXT
        )
        """.strip()
    )
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
    set_config(conn, cur, [
        ['LEAD_SW_ACTIVE', 1, 'リードスイッチの有効化'],
        ['DURATION', 10, 'カード認証時の最低開放期間']
    ], overwrite=False)
    
    
def set_config(conn, cur, ary, overwrite=True): # ary: [[key, value, note], ...]
    on_conflict = 'NOTHING'
    for key, val, note in ary:
        if overwrite:
            on_conflict = f'UPDATE SET Status={val}, Note=\"{note}\"'
        cur.execute(
            f"""
            INSERT INTO Config (Attribute, Status, Note)
            VALUES (\"{key}\", {val}, \"{note}\")
            ON CONFLICT(Attribute)
            DO {on_conflict}
            """.strip()
        )
    conn.commit()

def get_config(conn, cur, key):
    sql = f'SELECT * FROM Config WHERE Attribute = "{key}"'
    ary = [v for v in cur.execute(sql)]
    print(ary)
    if len(ary):
        _, val, _ = ary[0]
        return val
    return None
    

def confirm(txt):
    return qy.select(txt, choices=[
        qy.Choice(title='No', value=False),
        qy.Choice(title='Yes', value=True)
    ]).ask()