import json
import subprocess
import time

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
    
    
    
    
    
WS_CONTINUE = True

async def ws_handler(websocket):
    global WS_CONTINUE
    #name = await websocket.recv()
    for _ in range(60):
        await websocket.send('a')
        time.sleep(1)
    WS_CONTINUE = False
 
async def ws_main(host, port):
    async with websockets.serve(ws_handler, host, port):
        while True:
            if not WS_CONTINUE:
                break
            
def ws_init(host, port):
    global WS_CONTINUE
    WS_CONTINUE = True
    return ws_main(host, port)