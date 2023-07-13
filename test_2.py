
import time
from pirc522 import RFID
import RPi.GPIO as GPIO
from hashlib import md5
import os

LED_GREEN = 36
LED_RED   = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_GREEN, GPIO.OUT)
GPIO.setup(LED_RED  , GPIO.OUT)

GPIO.output(LED_GREEN, False)
GPIO.output(LED_RED  , True )

rdr = RFID()
util = rdr.util()
# Set util debug to true - it will print what's going on
#util.debug = True

def rfid_write_bytes(block, byte):
        util.do_auth(block)
        _byte = byte + bytearray((0,)) * (16 - len(byte))
        rdr.write(block, _byte)
        
def rfid_write_str(block, string):
        rfid_write_bytes(block, bytearray(string, 'utf-8'))

def rfid_read_bytes(block):
        util.do_auth(block)
        _, byte = rdr.read(block)
        return byte
    
def rfid_read_str(block):
        byte_array = rfid_read_bytes(block)
        dec_string = ""
        for character in byte_array:
                dec_string += chr(character)
        return dec_string

def toHex(byte_array):
    return ''.join(["{:02x}".format(b) for b in byte_array])

try:
  while True:
    # Wait for tag
    rdr.wait_for_tag()
    # Request tag
    (error, data) = rdr.request()
    if not error:
        os.system('clear')
        print("\nDetected")
        (error, uid) = rdr.anticoll()
        if not error:
            card_data = str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
            # Set tag as used in util. This will call RFID.select_tag(uid)
            util.set_tag(uid)
            # Save authorization info (key B) to util
            util.auth(rdr.auth_b, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])


            """
            text1='abcdefghijklmnopqrstwxyz'
            text2='0123456789'
            text3='test!'
            
            
            print("Writing new value...")
            rfid_write_str(4, text1)
            rfid_write_str(5, text2)
            rfid_write_str(6, text3)
            
            print("Printing results")
            print(rfid_read_str(4))
            print(rfid_read_bytes(4))
            print(rfid_read_str(5))
            print(rfid_read_bytes(5))
            print(rfid_read_str(6))
            print(rfid_read_bytes(6))
            """
            
            password = 'tsuden_id_XXXXXXXX'
            password_hash_md5 = md5(password.encode()).digest()
            _hash = toHex(list(password_hash_md5))
            print(f'Writing hashed-password... (password: "{password}")\n-> "{_hash}"')
            rfid_write_bytes(4, password_hash_md5)
            print('Done.\n' + '=' * 10)
            _record = toHex(rfid_read_bytes(4))
            res = _record == _hash
            print(f'  RFID Record     : {_record}')
            print(f'  Calculated Hash : {_hash}\n')
            print(f'  Result          : {res}\n' + '=' * 10)
            # We must stop crypto
            
            if res:
                GPIO.output(LED_GREEN, True)
                GPIO.output(LED_RED  , False)
            
            util.deauth()
            time.sleep(2)

            GPIO.output(LED_GREEN, False)
            GPIO.output(LED_RED  , True)
            print("Available to start a new reading.")

except KeyboardInterrupt:
  print('interrupted!')
finally:
  GPIO.cleanup()