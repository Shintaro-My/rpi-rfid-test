#!/usr/bin/env python

import signal
import time
import os
import sys
import sqlite3
from my_util import init_db, init_gpio, buzzer, led_green, led_red
from pirc522 import RFID
import RPi.GPIO as GPIO
import questionary as qy
from prettytable import PrettyTable as pt

DB_NAME = 'user.db'

def confirm(txt):
    return qy.select(txt, choices=[
        qy.Choice(title='No', value=False),
        qy.Choice(title='Yes', value=True)
    ]).ask()

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
        
        def read_card():
            rdr.wait_for_tag()

            (error, data) = rdr.request()
            if not error:
                print('=' * 10)
                print("\nDetected: " + format(data, "02x"))

                (error, uid) = rdr.anticoll()
                if not error:
                    _uid = '-'.join(['{:02x}'.format(u) for u in uid])
                    users = [v for v in cur.execute(f'SELECT * FROM Users WHERE UserId = "{_uid}"')]
                    if len(users):
                        _, name = users[0]
                        buzzer(2)
                        ex = qy.select(
                            f'The ID "{_uid}" is arleady registered as the user "{name}".',
                            choices=['(Cancel)', 'Rename', 'Delete']
                        ).ask()
                        if ex == 'Rename':
                            newname = qy.text('<ID: {_uid}>\n  Input new username:', default=name).ask()
                            cur.execute(f'UPDATE Users SET UserName = "{newname}" WHERE UserId = "{_uid}"')
                            conn.commit()
                            print('The user updated.')
                            led_green()
                            buzzer()
                        elif ex == 'Delete' and confirm(f'Are you sure you want to delete the user "{name}"?'):
                            cur.execute(f'DELETE FROM Users WHERE UserId = "{_uid}"')
                            conn.commit()
                            print('The user removed.')
                            led_green()
                            buzzer()
                    else:
                        buzzer(1)
                        name = ''
                        while name == '':
                            name = qy.text('<ID: {_uid}>\n  Input username:').ask()
                        
                    time.sleep(1)
                    led_red()
                    
        def show_users():
            users = [v for v in cur.execute(f'SELECT * FROM Users')]
            t = pt()
            t.field_names = ['UserId', 'UserName', 'Note']
            [t.add_row(u) for u in users]
            print(t.get_string())
            input('Continue to press Enter-key...')
                    
        def rename_user():
            users = [v for v in cur.execute(f'SELECT * FROM Users')]
            choices = [qy.Choice(title=f'{u[0]} ({u[1]})', value=i) for i, u in enumerate(users)]
            t = pt()
            t.field_names = ['UserId', 'UserName', 'Note']
            [t.add_row(u) for u in users]
            print(t.get_string())
            input('Continue to press Enter-key...')

        
        # main action
        while run:
            os.system('clear')
            opt = qy.select('Options', choices=[
                qy.Choice(title='Register', value=0),
                qy.Choice(title='Show Users', value=1),
                qy.Separator(''),
                qy.Separator('-- (DANGER) --'),
                qy.Choice(title='Rename User', value=2),
                qy.Choice(title='Delete User', value=3),
            ]).ask()
            if opt == 0:
                read_card()
            elif opt == 1:
                show_users()
            
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
        GPIO.cleanup()
    
#util.debug = True
if __name__ == '__main__':
    main()

