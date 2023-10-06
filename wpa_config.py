import re
import subprocess

BLANK = '        '

def create_pass(ssid, passphrase):
    cp = subprocess.run(
        f'wpa_passphrase {ssid} {passphrase}',
        shell=True,
        capture_output=True
    )
    txt = cp.stdout.decode().strip()[:-1] + f'{BLANK}key_mgmt=WPA-PSK'
    print(txt)

def splitter(ary):
    for i in range(0, len(ary), 2):
        yield ary[i:i+2]

if __name__ == '__main__':
    import sys
    n = len(sys.argv)
    if n % 2 == 0 or n == 1:
        raise Exception('引数の数が不正です。[ssid1, pass1, ssid2, pass2, ...]のように入力してください。')
    [create_pass(ssid, passphrase) for ssid, passphrase in splitter(sys.argv[1:])]


