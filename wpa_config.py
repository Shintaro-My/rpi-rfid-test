import re
import subprocess

def create_pass(ssid, passphrase):
    cp = subprocess.run(
        f'wpa_passphrase {ssid} {passphrase}',
        shell=True,
        capture_output=True
    )
    txt = cp.stdout.decode().strip()[:-1]
    print(txt)

if __name__ == '__main__':
    import sys
    _, ssid, passphrase = sys.argv
    create_pass(ssid, passphrase)


