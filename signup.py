#!/usr/bin/env python

import signal
import time
import traceback
import os
import sys
import sqlite3
from my_util import init_db, init_gpio, buzzer, led_green, led_red
from pirc522 import RFID
import RPi.GPIO as GPIO
import questionary as qy
from prettytable import PrettyTable as pt
import keyboard

DB_NAME = 'user.db'

def confirm(txt):
    return qy.select(txt, choices=[
        qy.Choice(title='No', value=False),
        qy.Choice(title='Yes', value=True)
    ]).ask()

def main():
    init_gpio()
    led_red()
    buzzer()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    rdr = RFID()
    util = rdr.util()

    try:
        init_db(conn, cur)
        #users = [v for v in cur.execute('SELECT * FROM Users')]
        #print(users)
        print("Starting")
        
        def read_card():
            while True:
                rdr.wait_for_tag()

                (error, data) = rdr.request()
                if not error:
                    (error, uid) = rdr.anticoll()
                    if not error:
                        _uid = '-'.join(['{:02x}'.format(u) for u in uid])
                        users = [v for v in cur.execute(f'SELECT * FROM Users WHERE UserId = "{_uid}"')]
                        print('=' * 10)
                        if len(users):
                            _, name = users[0][:2]
                            buzzer(2)
                            ex = qy.select(
                                f'The ID "{_uid}" is arleady registered as the user "{name}".',
                                choices=['(Cancel)', 'Rename', 'Delete']
                            ).ask()
                            if ex == 'Rename':
                                newname = qy.text(f'<ID: {_uid}>\n  Input new username:', default=name).ask()
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
                                name = qy.text(f'<ID: {_uid}>\n  Input username:').ask()

                            cur.execute(f'INSERT INTO Users values("{_uid}", "{name}", "")')
                            conn.commit()
                            print('The user registered.')
                            led_green()
                            buzzer()
                            
                        time.sleep(1)
                        led_red()
                        break
                    
        def _get_user_table():
            users = [v for v in cur.execute(f'SELECT * FROM Users')]
            t = pt()
            t.field_names = ['UserId', 'UserName', 'Note']
            [t.add_row(u) for u in users]
            return t, users
            
        def show_users():
            t, _ = _get_user_table()
            print(t.get_string())
            input('Continue to press Enter-key...')
                    
        def _select_user():
            t, users = _get_user_table()
            choices = []
            for r in t: r.header = False
            a, b, c, *ary, z = t.get_string().split('\n')
            for i, l in enumerate(ary):
                choices += [qy.Choice(title=l, value=i)]
            choices += [qy.Separator(z)]
            index = qy.select(f'test\n   {a}\n   {b}\n   {c}', choices=choices).ask()
            os.system('clear')
            return users[index]
        
        def rename_user():
            uid, name, _ = _select_user()
            newname = qy.text(f'<ID: {uid}>\n  Input new username:', default=name).ask()
            cur.execute(f'UPDATE Users SET UserName = "{newname}" WHERE UserId = "{uid}"')
            conn.commit()
            print('The user updated.')
            led_green()
            buzzer()
        
        def delete_user():
            uid, name, _ = _select_user()
            if confirm(f'Are you sure you want to delete the user "{name}"?'):
                cur.execute(f'DELETE FROM Users WHERE UserId = "{uid}"')
                conn.commit()
                print('The user removed.')
                led_green()
                buzzer()
        
        # main action
        while True:
            os.system('clear')
            opt = qy.select('Options', choices=[
                qy.Choice(title='Register', value=0),
                qy.Choice(title='Show Users', value=1),
                qy.Choice(title='Exit *', value=-1),
                qy.Separator('______________'),
                qy.Separator('-- (DANGER) --'),
                qy.Choice(title='Rename User', value=2),
                qy.Choice(title='Delete User', value=3),
            ]).ask()
            
            if opt == -1:
                break
            elif opt == 0:
                read_card()
            elif opt == 1:
                show_users()
            elif opt == 2:
                rename_user()
            elif opt == 3:
                delete_user()
                
            time.sleep(2)
            
    except Exception as e:
        t = traceback.format_exc()
        print(t)
    finally:
        cur.close()
        conn.close()
        GPIO.cleanup()
        rdr.cleanup()
        sys.exit()
    
#util.debug = True
if __name__ == '__main__':
    main()

