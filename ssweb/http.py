import socket
import threading
import re

class Http:

    global http_methods
    http_methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'PATCH', 'CONNECT', 'OPTIONS', 'TRACE']

    def __init__(self, target, port):
        self.target = target
        self.port = port

    def handle_conn(self, c, addr):
        global http_methods
        print("[*] Connection from: %s:%s" % (addr[0], addr[1]))
        chunks = []
        while True:
            data = c.recv(2048)
            if not data:
                break
            chunks.append(data.replace(b'\r\n', b'\n'))
            print("%s" % (chunks))
            if(len(chunks) > 2):
                if(chunks[-1] == b'\n'):
                    break
        req = (b''.join(chunks)).decode('utf-8')
        hdrs,body = req.split('\n\n')
        headers = hdrs.split('\n')
        method = headers.pop(0)
        allowed_re = '|'.join(http_methods)
        if(re.search((r"(%s)\s(\/\S*)\sHTTP" % allowed_re), method) is not None):
            for h in headers:
                if(re.search('[^\:]+\:\s.*', h) is None):
                   c.send("disallowed requestaa".encode('utf-8'))
                else:
                    self.parse_http(c, method, headers, body) # not implemented yet
        else:
           c.send("disallowed requestbb".encode('utf-8'))

    def deploy_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.target, self.port))
        s.listen()
        print("[*] Listening on: %s:%s" % (self.target, self.port))
        while True:
            client,addr = s.accept()

            client_thread = threading.Thread(target=self.handle_conn, args=(client,addr))
            client_thread.start()


