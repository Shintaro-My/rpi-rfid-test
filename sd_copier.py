import json
import subprocess

_cmd = lambda c: subprocess.run(
    c.split(), 
    capture_output=True,
    text=True
)

def lsblk():
    process = _cmd('/usr/bin/lsblk --json -o NAME,MOUNTPOINT')
    blockdevices = json.loads(process.stdout)['blockdevices']
    return blockdevices