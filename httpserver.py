from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import os
import subprocess
import traceback
import re
import magic # python-magic
# import socket
import sqlite3
from my_util import init_db, DB_NAME, set_config
import mycmd
import ipget
import time



#IP = socket.gethostbyname(socket.gethostname())
IP = None
for i in range(10):
    try:
        IP, _ = ipget.ipget().ipaddr('wlan0').split('/')
        if IP: break
    except:
        print('Searching IP...')
        time.sleep(1)
        continue
if not IP: raise Exception('Not Connected')
current_dir = ''

# CHANGE_DISABLE = False
BACKUP_TARGET = False
CMD_THREAD = None
SERVER_PAUSE = False


class _MyHandler(BaseHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        BaseHTTPRequestHandler.end_headers(self)
        
    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        print(query)
        
        isMatch, status, txt = _Page_DELETE(self, path, query)
        if isMatch:
            self.send_response(status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(txt.encode("utf-8"))
        else:
            self.send_error(404)
            
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        print(query)
        
        isMatch, status, txt = _Page_GET(self, path, query)
        if isMatch:
            self.send_response(status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(txt.encode("utf-8"))
        else:
            try:
                v = re.split(r'\/|\\', path)[1:]
                fpath = os.path.join(current_dir, *v)
                with open(fpath, 'rb') as f:
                    buff = f.read()
                    _mime = _getMimeFromExt(fpath)
                    _mime = _mime if _mime else magic.from_buffer(buff, mime=True)
                    self.send_response(200)
                    self.send_header('Content-type', _mime)
                    self.end_headers()
                    self.wfile.write(buff)
                    return
            except IOError:
                self.send_error(404)
        
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        print(query)
        
        content_length = int(self.headers['content-length'])
        _body = self.rfile.read(content_length).decode('utf-8')
        body = json.loads(_body)
        print(body)
        
        isMatch, status, txt = _Page_POST(self, path, query, body)
        if isMatch:
            self.send_response(status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(txt.encode("utf-8"))
        else:
            self.send_error(404)
            
    def do_PUT(self):
        global BACKUP_TARGET, CMD_THREAD
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        print(query)
        
        ######## EX ########
        if path == '/backup' and 'disk' in query:
            if CMD_THREAD:
                if CMD_THREAD.is_alive():
                    txt = json.dumps({'status': 'err', 'body': 'Backup in progress...'})
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(txt.encode("utf-8"))
                    return
                else:
                    CMD_THREAD.join()
                    CMD_THREAD = None
            BACKUP_TARGET, = query['disk']
            #command = ['sh', './test.sh']
            command = ['sudo', 'rpi-clone', BACKUP_TARGET, '-U']
            CMD_THREAD = threading.Thread(
                target=mycmd.cmd_realtime,
                args=(command,),
                daemon=True
            )
            CMD_THREAD.start()
            txt = json.dumps({'status': 'ok', 'body': f'Backup starting: {BACKUP_TARGET}'})
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(txt.encode("utf-8"))
            return
        ######## EX ########

        self.send_error(404)
            
class Server:
    def __init__(self, port=8080) -> None:
        host = IP
        self.httpd = HTTPServer((host, port), _MyHandler)
        print(f'serving at http://{host}:{port}')
    def listen(self):
        if SERVER_PAUSE:
            time.sleep(.1)
        else:
            self.httpd.handle_request()
        
def _getMimeFromExt(path):
    if path.endswith('.css'):
        return 'text/css'
    elif path.endswith('.js'):
        return 'text/javascript'
    return None
    

def _Page_GET(self: _MyHandler, path, query):
    global CMD_THREAD
    data = {'status': 'ok'}
    status = 200
    
    if path == '/':
        try:
            data['body'] = {}
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        return (True, status, json.dumps(data))

    elif path == '/backup':
        if CMD_THREAD:
            if CMD_THREAD.is_alive():
                data['status'] = 'await'
                data['body'] = 'Backup in progress...'
                status = 401
                return (True, status, json.dumps(data))
            else:
                CMD_THREAD.join()
                CMD_THREAD = None
        data['body'] = True
        return (True, status, json.dumps(data))
                
    elif path == '/lsblk':
        try:
            lsblk = mycmd.lsblk()
            data['body'] = lsblk
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        return (True, status, json.dumps(data))
    
    elif path == '/forceopen':
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            init_db(conn, cur)
            set_config(conn, cur, [['FORCE_OPEN', 1, '']])
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
    
    elif path == '/config':
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            init_db(conn, cur)
            sql = 'SELECT * FROM Config'
            if 'attribute' in query:
                attr, = query["attribute"]
                sql += f' WHERE Attribute = "{attr}"'
            data['body'] = [v for v in cur.execute(sql)]
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
    
    elif path == '/users':
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            init_db(conn, cur)
            sql = 'SELECT * FROM Users'
            if 'id' in query:
                uid, = query["id"]
                sql += f' WHERE UserId = "{uid}"'
            data['body'] = [v for v in cur.execute(sql)]
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
        
    elif path == '/anonymous':
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            init_db(conn, cur)
            sql = 'SELECT * FROM Anonymous'
            if 'id' in query:
                uid, = query["id"]
                sql += f' WHERE UserId = "{uid}"'
            data['body'] = [v for v in cur.execute(sql)]
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
        
    return (False, 404, None)
    
    
def _Page_POST(self: _MyHandler, path, query, body: dict={}):        
    data = {'status': 'ok'}
    status = 200
    
    
    if path == '/users':
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            init_db(conn, cur)
            uid, uname, note = (body.get(k) for k in ('UserId', 'UserName', 'Note'))
            cur.execute(
                f"""
                INSERT INTO Users (UserId, UserName, Note, CreatedAt, LastSeen)
                VALUES (\"{uid}\", \"{uname}\", \"{note}\", datetime('now', '+9 hours'), datetime('now', '+9 hours'))
                ON CONFLICT(UserId)
                DO UPDATE SET UserName=\"{uname}\", Note=\"{note}\"
                """.strip()
            )
            conn.commit()
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
        
    elif path == '/config':
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            init_db(conn, cur)
            attr, stat, note = (body.get(k) for k in ('Attribute', 'Status', 'Note'))
            
            print(attr)
            print(stat)
            print(note)
            
            set_config(conn, cur, [[attr, stat, note]], True)
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
        
    elif path == '/restore':
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            cur.execute("DROP TABLE IF EXISTS Users")
            cur.execute("DROP TABLE IF EXISTS Anonymous")
            init_db(conn, cur)
            users = body.get('Users')
            for user in users:
                uid, uname, note, createdat, lastseen = (user.get(k) for k in ('UserId', 'UserName', 'Note', 'CreatedAt', 'LastSeen'))
                cur.execute(
                    f"""
                    INSERT INTO Users (UserId, UserName, Note, CreatedAt, LastSeen)
                    VALUES (\"{uid}\", \"{uname}\", \"{note}\", \"{createdat}\", \"{lastseen}\")
                    """.strip()
                )
            conn.commit()
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
        
    else:
        return (False, 404, None)
    
    
def _Page_DELETE(self: _MyHandler, path, query):
    data = {'status': 'ok'}
    status = 200
    
    if path == '/users' and 'id' in query:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            uids, = query["id"]
            uids = [f'UserId = "{uid}"' for uid in uids.split(',')]
            cur.execute(f'DELETE FROM Users WHERE {" OR ".join(uids)}')
            conn.commit()
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
    elif path == '/config' and 'attribute' in query:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            attributes, = query["attribute"]
            attributes = [f'Attribute = "{attr}"' for attr in attributes.split(',')]
            cur.execute(f'DELETE FROM Config WHERE {" OR ".join(attributes)}')
            conn.commit()
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
    elif path == '/anonymous' and 'id' in query:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            uids, = query["id"]
            uids = [f'UserId = "{uid}"' for uid in uids.split(',')]
            cur.execute(f'DELETE FROM Anonymous WHERE {" OR ".join(uids)}')
            conn.commit()
        except Exception as e:
            data['status'] = 'err'
            t = traceback.format_exc()
            print(t)
            data['body'] = t
            status = 500
        finally:
            cur.close()
            conn.close()
            return (True, status, json.dumps(data))
    elif path == '/shutdown' and 'mode' in query:
        mode, = query['mode']
        if mode == 'h' and 'time' in query:
            timing, = query['time']
            if type(timing) == int:
                timing = f'+{timing}'
            cmd = f"sudo shutdown -h {timing}"
            subprocess.call(cmd, shell=True)
            return (True, status, json.dumps(data))
        elif mode == 'c':
            cmd = "sudo shutdown -c"
            subprocess.call(cmd, shell=True)
            return (True, status, json.dumps(data))
    elif path == '/reboot':
        cmd = "sudo reboot"
        subprocess.call(cmd, shell=True)
        return (True, status, json.dumps(data))
    else:
        return (False, 404, None)
    
    
if __name__ == '__main__':
    import time
    import threading
    time.sleep(.5)
    server = Server(12345)
    # mycmd.cmd_with_websocket(WS_SERVER, [])
   
    
    while True:
        try:
            server.listen()
        except KeyboardInterrupt:
            print('\nAbort.')
            break
    