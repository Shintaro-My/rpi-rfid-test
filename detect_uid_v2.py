#!/usr/bin/env python

import signal
import time
import threading
import sys
import sqlite3
from my_util import init_db, init_gpio, buzzer, led_green, led_red, led_all_off, led_all_on, DB_NAME, relay, is_door_open, get_config, set_config
#from pirc522 import RFID
from mfrc522_i2c import MFRC522
import RPi.GPIO as GPIO

DURATION = 10

START_TIME = None
BEFORE_UID = None

REED_SW_ACTIVE = 1

run = True
_relay_stat = False

def main(conn: sqlite3.Connection, cur: sqlite3.Cursor):
    global BEFORE_UID, START_TIME, REED_SW_ACTIVE, DURATION, _relay_stat, run
    
    init_gpio()
    
    try:
        REED_SW_ACTIVE = get_config(conn, cur, 'REED_SW_ACTIVE')
        DURATION = get_config(conn, cur, 'DURATION')
    except Exception as e:
        print(0)
        print(e)

    led_red()
    buzzer()

    #rdr = RFID()
    #util = rdr.util()
    i2cBus = 1
    i2cAddress = 0x28

    # Create an object of the class MFRC522
    MFRC522Reader = MFRC522(i2cBus, i2cAddress)
    version = MFRC522Reader.getReaderVersion()
    print(f'MFRC522 Software Version: {version}')

    try:
        def end_read(signal, frame):
            global run
            print("\nCtrl+C captured, ending read.")
            run = False
            #rdr.cleanup()
            GPIO.cleanup()
            sys.exit()
        
        def tick():
            global _relay_stat, run, START_TIME
            n = 0
            try:
                _conn = sqlite3.connect(DB_NAME)
                _cur = _conn.cursor()
                init_gpio()
            except Exception as e:
                print(2)
                print(e)
            while run:
                if _relay_stat:
                    relay(True)
                else:
                    try:
                        init_db(_conn, _cur)
                        _open = get_config(_conn, _cur, 'FORCE_OPEN')
                        if _open:
                            print('\n' + '=' * 10)
                            print('[!] force open')
                            START_TIME = time.time()
                            set_config(_conn, _cur, [ ['FORCE_OPEN', 0, ''] ])
                            buzzer()
                    except Exception as e:
                        print(1)
                        print(e)

                    if REED_SW_ACTIVE:
                        if is_door_open():
                            n += 1
                            if 40 <= n:
                                print('!')
                                n = 0
                            else:
                                print('!', end='')
                            relay(True)
                        else:
                            relay(False)
                    else:
                        relay(False)
                        
                time.sleep(0.075)
                
            if _cur: _cur.close()
            if _conn: _conn.close()

        signal.signal(signal.SIGINT, end_read)
        tick_thread = threading.Thread(target=tick)

        led_all_off()

        tick_thread.start()

        
        while run:
            try:
                (status, backData, tagType) = MFRC522Reader.scan()
                if status == MFRC522Reader.MIFARE_OK:
                    print('\n' + '=' * 10)
                    (status, uid, backBits) = MFRC522Reader.identify()
                    print(f'TagType: {tagType}')
                    if status == MFRC522Reader.MIFARE_OK:
                        _uid = '-'.join(['{:02x}'.format(u) for u in uid])
                        auth(conn, cur, _uid)

                if not START_TIME:
                    BEFORE_UID = None
                elif (time.time() - START_TIME) < DURATION:
                    _relay_stat = True
                    led_green()
                else:
                    _relay_stat = False
                    led_all_off()
                    START_TIME = None
            except IOError as e:
                print('io')
                print(e)
               
    except Exception as e:
        print(3)
        print(e)
    finally:
        tick_thread.join()
        GPIO.cleanup()
        return True
    
def auth(conn: sqlite3.Connection, cur: sqlite3.Cursor, uid):
    global BEFORE_UID, START_TIME

    print(f"ID: {uid}")

    
    try:
        users = [v for v in cur.execute(f'SELECT * FROM Users WHERE UserId = "{uid}"')]
        if len(users):
            _, name = users[0][:2]
            if BEFORE_UID != uid:
                cur.execute(
                    f"""
                    UPDATE Users SET LastSeen=datetime('now', '+9 hours') WHERE UserId="{uid}"
                    """.strip()
                )
                conn.commit()
                print(f'Welcome, "{name}" <ID: {uid}>!')
            else:
                print('(repeat)')
            START_TIME = time.time()
            buzzer()
        else:
            buzzer(2, led_red, led_all_off)
            led_red()
            if BEFORE_UID != uid:
                print('[!] Invalid User.')
                cur.execute(
                    f"""
                    INSERT INTO Anonymous (UserId, LastUpdate)
                    VALUES (\"{uid}\", datetime('now', '+9 hours'))
                    ON CONFLICT(UserId)
                    DO UPDATE SET LastUpdate=datetime('now', '+9 hours')
                    """.strip()
                )
                conn.commit()
            else:
                print('(repeat)')
            time.sleep(.1)
            led_all_off()
    except Exception as e:
        print(4)
        print(e)

    BEFORE_UID = uid

#util.debug = True
if __name__ == '__main__':
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        init_db(conn, cur)
        main(conn, cur)
    except Exception as e:
        print(5)
        print(e)
    finally:
        if cur: cur.close()
        if conn: conn.close()