import re
import subprocess

WPA_HEADER = """
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
""".strip()
BLANK = '        '

def create_pass(ssid, passphrase, priority=None):
    n = len(passphrase)
    if n < 8 or 63 < n:
        raise Exception(f'パスワードは 8 - 64 文字です: ["{ssid}" / "{passphrase}]')
    cp = subprocess.run(
        f'ss="{ssid}" && ps="{passphrase}" && ' + 'wpa_passphrase "${ss}" "${ps}"',
        shell=True,
        capture_output=True
    )
    attr = ['key_mgmt=WPA-PSK']
    if priority is not None:
        attr += [f'priority={priority}']
    txt = cp.stdout.decode().strip()[:-1] + '\n'.join([f'{BLANK}{a}' for a in attr]) + '\n}'
    return txt

def splitter(ary):
    for i in range(0, len(ary), 2):
        yield ary[i:i+2]

if __name__ == '__main__':
    import sys
    n = len(sys.argv)
    if n % 2 == 0 or n == 1:
        raise Exception('引数の数が不正です。[ssid1, pass1, ssid2, pass2, ...]のように入力してください。')
    networks = [create_pass(*sp, priority=i) for i, sp in enumerate(splitter(sys.argv[1:]))]
    context = WPA_HEADER + '\n\n' + '\n'.join(networks) + '\n'
    
    with open('_temp.txt', 'w') as f:
        f.write(context)
    
    cp = subprocess.run(
        'cat _temp.txt',
        shell=True,
        capture_output=True
    )
    
    print(cp.stdout.decode())