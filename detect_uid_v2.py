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

LEAD_SW_ACTIVE = 1


_relay_stat = False

def main():
    global BEFORE_UID, START_TIME, LEAD_SW_ACTIVE, DURATION, _relay_stat
    
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        init_db(conn, cur)
        LEAD_SW_ACTIVE = get_config(conn, cur, 'LEAD_SW_ACTIVE')
        DURATION = get_config(conn, cur, 'DURATION')
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    
    init_gpio()
    led_red()
    buzzer()


    run = True
    #rdr = RFID()
    #util = rdr.util()
    i2cBus = 1
    i2cAddress = 0x28

    # Create an object of the class MFRC522
    MFRC522Reader = MFRC522(i2cBus, i2cAddress)
    version = MFRC522Reader.getReaderVersion()
    print(f'MFRC522 Software Version: {version}')

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        init_db(conn, cur)
        cur.close()
        conn.close()
        #users = [v for v in cur.execute('SELECT * FROM Users')]
        #print(users)
        def end_read(signal,frame):
            global run
            print("\nCtrl+C captured, ending read.")
            run = False
            #rdr.cleanup()
            sys.exit()
        
        
        def tick():
            global _relay_stat, run
            while run:
                if _relay_stat:
                    relay(True)
                else:
                    if LEAD_SW_ACTIVE:
                        if is_door_open():
                            relay(True)
                        else:
                            relay(False)
                time.sleep(0.05)
        
        def check_id():
            global _relay_stat, run, BEFORE_UID, START_TIME
            while run:
                (status, backData, tagType) = MFRC522Reader.scan()
                if status == MFRC522Reader.MIFARE_OK:
                    print('=' * 10)
                    (status, uid, backBits) = MFRC522Reader.identify()
                    if status == MFRC522Reader.MIFARE_OK:
                        _uid = '-'.join(['{:02x}'.format(u) for u in uid])
                        print(f"ID: {_uid}")
                        auth(_uid)
                
                elif not START_TIME:
                    BEFORE_UID = None
                elif (time.time() - START_TIME) < DURATION:
                    _relay_stat = True
                    led_green()
                else:
                    _relay_stat = False
                    led_all_off()
                    START_TIME = None
            

        signal.signal(signal.SIGINT, end_read)
        tick_thread = threading.Thread(target=tick)
        check_id_thread = threading.Thread(target=check_id)

        led_all_off()

        tick_thread.start()
        check_id_thread.start()

                        
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
        GPIO.cleanup()
        tick_thread.join()
        check_id_thread.join()
        return True
    
def auth(uid):
    global BEFORE_UID, START_TIME
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
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
            cur.close()
            conn.close()
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
            cur.close()
            conn.close()
        else:
            print('(repeat)')
        time.sleep(.2)
        led_all_off()
        
    BEFORE_UID = uid

#util.debug = True
if __name__ == '__main__':
    main()
