#!/usr/bin/env python

import signal
import time
import sys
import sqlite3
from my_util import init_db, init_gpio, buzzer, led_green, led_red, led_all_off, DB_NAME, relay
#from pirc522 import RFID
from mfrc522_i2c import MFRC522
import RPi.GPIO as GPIO
import asyncio

DURATION = 3

def main():
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

        signal.signal(signal.SIGINT, end_read)


        while run:
            (status, backData, tagType) = MFRC522Reader.scan()
            if status == MFRC522Reader.MIFARE_OK:
                print('=' * 10)
                (status, uid, backBits) = MFRC522Reader.identify()
                if status == MFRC522Reader.MIFARE_OK:
                    _uid = '-'.join(['{:02x}'.format(u) for u in uid])
                    print(f"ID: {_uid}")
                    auth(_uid)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
        GPIO.cleanup()
        return True
    
async def auth(uid):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    users = [v for v in cur.execute(f'SELECT * FROM Users WHERE UserId = "{uid}"')]
    if len(users):
        cur.execute(
            f"""
            UPDATE Users SET LastSeen=datetime('now', '+9 hours') WHERE UserId="{uid}"
            """.strip()
        )
        conn.commit()
        cur.close()
        conn.close()
        _, name = users[0][:2]
        print(f'Welcome, "{name}" <ID: {uid}>!')
        relay(True)
        led_green()
        buzzer()
        await asyncio.sleep(DURATION)
        relay(False)
        led_all_off()
    else:
        buzzer(2, led_red, led_all_off)
        led_red()
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
        
    time.sleep(1)

#util.debug = True
if __name__ == '__main__':
    main()
