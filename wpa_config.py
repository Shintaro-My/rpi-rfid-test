import re
import subprocess

def create_pass(ssid, passphrase):
    cp = subprocess.run(
        f'wpa_passphrase {ssid} {passphrase}',
        capture_output=True
    )
    txt = cp.stdout[-1]
    print(txt)

if __name__ == '__main__':
    import sys
    ssid, passphrase = sys.argv
    create_pass(ssid, passphrase)


