from mfrc522_i2c import MFRC522
import signal
import RPi.GPIO as GPIO
from hashlib import md5, sha256
import os

import random
import string

random_str = lambda num: ''.join(random.choices(string.ascii_letters + string.digits, k=num))

LED_GREEN = 36
LED_RED   = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_GREEN, GPIO.OUT)
GPIO.setup(LED_RED  , GPIO.OUT)

GPIO.output(LED_GREEN, False)
GPIO.output(LED_RED  , True )


continue_reading = True


def end_read(signal, frame):
    """ Capture SIGINT for cleanup when script is aborted """
    global continue_reading
    print('Ctrl+C captured, ending read')
    continue_reading = False


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Reader is located at Bus 1, adress 0x28
i2cBus = 1
i2cAddress = 0x28

# Create an object of the class MFRC522
MFRC522Reader = MFRC522(i2cBus, i2cAddress)

version = MFRC522Reader.getReaderVersion()
print(f'MFRC522 Software Version: {version}')





def toHex(byte_array):
    return ''.join(["{:02x}".format(b) for b in byte_array])

# https://github.com/cpranzl/mfrc522_i2c/blob/main/examples/read.py
try:
  while continue_reading:
    # Scan for cards
    (status, backData, tagType) = MFRC522Reader.scan()
    if status == MFRC522Reader.MIFARE_OK:
        print(f'Card detected, Type: {tagType}')

        # Get UID of the card
        (status, uid, backBits) = MFRC522Reader.identify()
        if status == MFRC522Reader.MIFARE_OK:
            print('Card identified, UID: ', end='')
            for i in range(0, len(uid) - 1):
                print(f'{uid[i]:02x}:', end='')
            print(f'{uid[len(uid) - 1]:02x}')

            # Select the scanned card
            (status, backData, backBits) = MFRC522Reader.select(uid)
            if status == MFRC522Reader.MIFARE_OK:
                print('Card selected')

                # TODO: Determine 1K or 4K

                # Authenticate
                blockAddr = 8
                (status, backData, backBits) = MFRC522Reader.authenticate(
                    MFRC522Reader.MIFARE_AUTHKEY1,
                    blockAddr,
                    MFRC522Reader.MIFARE_KEY,
                    uid)
                if (status == MFRC522Reader.MIFARE_OK):
                    print('Card authenticated')

                    # Read data from card
                    (status, backData, backBits) = MFRC522Reader.read(
                        blockAddr)
                    if (status == MFRC522Reader.MIFARE_OK):
                        print(f'Block {blockAddr:02} : ', end='')
                        for i in range(0, len(backData)):
                            print(f'{backData[i]:02x} ', end='')
                        print('read')

                        continue_reading = False
                    else:
                        print('Error while reading')

                    # Deauthenticate
                    MFRC522Reader.deauthenticate()
                    print('Card deauthenticated')
                else:
                    print('Authentication error')
      
"""
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
"""
            password = f'tsuden_{random_str(8)}'
            password_hash = sha256(password.encode()).digest()
            _hash = toHex(list(password_hash))
            print(f'Writing hashed-password... (password: "{password}")\n-> "{_hash}"')
            
            #rfid_write_str(4, 'my_user_id')
            rfid_write_bytes(5, password_hash[:16])
            rfid_write_bytes(6, password_hash[16:])
            print('Done.\n' + '=' * 10)
            
            #user_id = rfid_read_str(4)
            _record = toHex(rfid_read_bytes(5) + rfid_read_bytes(6))
            res = _record == _hash
            print(f'  Hash        : {_hash}')
            print(f'  RFID Record : {_record}\n')
            print(f'  Result      : {res}\n' + '=' * 10)
            # We must stop crypto
            
            if res:
                GPIO.output(LED_GREEN, True)
                GPIO.output(LED_RED  , False)
            
            util.deauth()
            time.sleep(1)

            GPIO.output(LED_GREEN, False)
            GPIO.output(LED_RED  , True)
            print("Available to start a new reading.")
"""
except KeyboardInterrupt:
  print('(interrupted)')
finally:
  GPIO.cleanup()
