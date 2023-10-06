import re
import subprocess

BLANK = '        '

def create_pass(ssid, passphrase, priority=None):
    cp = subprocess.run(
        f'wpa_passphrase {ssid} {passphrase}',
        shell=True,
        capture_output=True
    )
    attr = ['key_mgmt=WPA-PSK']
    if priority is not None:
        attr += [f'priority={priority}']
    txt = cp.stdout.decode().strip()[:-1] + '\n'.join([f'{BLANK}{a}' for a in attr])
    print(txt)
    return txt

def splitter(ary):
    for i in range(0, len(ary), 2):
        yield ary[i:i+2]

if __name__ == '__main__':
    import sys
    n = len(sys.argv)
    if n % 2 == 0 or n == 1:
        raise Exception('引数の数が不正です。[ssid1, pass1, ssid2, pass2, ...]のように入力してください。')
    [create_pass(*sp, priority=i) for i, sp in enumerate(splitter(sys.argv[1:]))]


