import json
import subprocess
import time

import sys
import asyncio
import websockets
 

_cmd = lambda c: subprocess.run(
    c.split(), 
    capture_output=True,
    text=True
)

def _cmd_realtime(cmd):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    while True:
        line = process.stdout.readline()
        if line:
            yield line
        elif process.poll() is not None:
            break

def lsblk():
    process = _cmd('/usr/bin/lsblk --json -o NAME,MOUNTPOINT')
    blockdevices = json.loads(process.stdout)['blockdevices']
    return blockdevices

def start_streaming(handler):
    handler.send_response(200)
    handler.send_header('Connection', 'Keep-Alive')
    handler.send_header('Content-Type', 'text/event-stream')
    handler.end_headers()
    
    for _ in range(10):
        value = str(time.time()).encode('UTF-8')
        handler.wfile.write(b'name: ')
        handler.wfile.write(b'stream')
        handler.wfile.write(b'\r\n')
        handler.wfile.write(b'data: ')
        handler.wfile.write(value)
        handler.wfile.write(b'\r\n')
        handler.wfile.flush()
        time.sleep(1)
        
    handler.wfile.close()
    
    
async def cmd_promise_with_websocket(websocket, cmd):
    # await asyncio.create_subprocess_exec
    proc = subprocess.Popen(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    while True:
        stdout = proc.stdout.readline()
        if stdout:
            txt = stdout.decode('UTF-8', 'replace')
            print(f'[stdout] {txt}', end='', flush=True)
            await websocket.send(json.dumps({'data': txt, 'type': 'stdout'}))
        elif proc.poll() is not None:
            break
        time.sleep(.1)
    
WS_CONTINUE = True
 
async def ws_main(host, port, disk):

    async def ws_handler(websocket):
        global WS_CONTINUE
        #name = await websocket.recv()
        """
        for _ in range(15):
            await websocket.send(str(time.time()))
            time.sleep(1)
        """
        command = ['sh', './test.sh']
        # command = ['sudo', 'rpi-clone', disk, '-U']
        await websocket.send(json.dumps({'data': " ".join(command), 'type': 'cmd'}))
        await cmd_promise_with_websocket(websocket, command)
        WS_CONTINUE = False
        
    async with websockets.serve(ws_handler, host, port):
        while True:
            if WS_CONTINUE:
                await asyncio.sleep(0.01)
            else:
                break
            
def ws_init(host, port, disk):
    global WS_CONTINUE
    WS_CONTINUE = True
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ws_main(host, port, disk))
    loop.close()
    return