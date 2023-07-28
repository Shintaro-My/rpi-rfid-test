from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import os
import traceback
import re
import magic # python-magic
import socket
import sqlite3
from my_util import init_db, DB_NAME
import ipget

#IP = socket.gethostbyname(socket.gethostname())
IP, _ = ipget.ipget().ipaddr('wlan0').split('/')
current_dir = ''

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
            

class Server:
    def __init__(self, port=8080) -> None:
        host = IP
        self.httpd = HTTPServer((host, port), _MyHandler)
        print(f'serving at http://{host}:{port}')
    def listen(self):
        self.httpd.handle_request()
        

def _getMimeFromExt(path):
    if path.endswith('.css'):
        return 'text/css'
    elif path.endswith('.js'):
        return 'text/javascript'
    return None
    

def _Page_GET(self: _MyHandler, path, query):
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
        
    else:
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
    else:
        return (False, 404, None)
    
    
if __name__ == '__main__':
    import time
    time.sleep(3)
    server = Server(12345)
    while True:
        try:
            server.listen()
        except KeyboardInterrupt:
            print('\nAbort.')
            break