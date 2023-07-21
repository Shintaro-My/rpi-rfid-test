#!/usr/bin/env python

import signal
import time
import sys
import sqlite3
from my_util import init_db, init_gpio, buzzer, led_green, led_red
from pirc522 import RFID
import RPi.GPIO as GPIO

DB_NAME = 'user.db'

        

def main():
    init_gpio()
    led_red()
    buzzer(3)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    run = True
    rdr = RFID()
    util = rdr.util()

    try:
        init_db(conn, cur)
        #users = [v for v in cur.execute('SELECT * FROM Users')]
        #print(users)
        def end_read(signal,frame):
            global run
            print("\nCtrl+C captured, ending read.")
            run = False
            rdr.cleanup()
            sys.exit()

        signal.signal(signal.SIGINT, end_read)

        print("Starting")
        while run:
            rdr.wait_for_tag()

            (error, data) = rdr.request()
            if not error:
                print('=' * 10)
                print("\nDetected: " + format(data, "02x"))

                (error, uid) = rdr.anticoll()
                if not error:
                    _uid = '-'.join(['{:02x}'.format(u) for u in uid])
                    print(f"ID: {_uid}")
                    users = [v for v in cur.execute(f'SELECT * FROM Users WHERE UserId = "{_uid}"')]
                    if len(users):
                        _, name = users[0]
                        print(f'Welcome, "{name}" <ID: {_uid}>!')
                        led_green()
                        buzzer()
                        time.sleep(5)
                        led_red()
                    else:
                        buzzer(2)
                        print('[!] Invalid User.')
                    time.sleep(1)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
        GPIO.cleanup()
    
#util.debug = True
if __name__ == '__main__':
    main()
