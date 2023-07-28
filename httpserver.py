from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import os
import re
import magic # python-magic
import socket

IP = socket.gethostbyname(socket.gethostname())
current_dir = ''

class _MyHandler(BaseHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        BaseHTTPRequestHandler.end_headers(self)
        
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
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
    return None
    

def _Page_GET(self: _MyHandler, path, query):
    data = {'status': 'ok'}
    
    if path == '/':
        status = 200
        try:
            data['body'] = {}
        except Exception as e:
            data['status'] = 'err'
            data['body'] = str(e)
            status = 500
        return (True, status, json.dumps(data))
    else:
        return (False, 404, None)
    
    
    
if __name__ == '__main__':
    server = Server()
    while True:
        try:
            server.listen()
        except KeyboardInterrupt:
            print('\nAbort.')
            break