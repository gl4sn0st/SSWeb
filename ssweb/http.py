import socket
from multiprocessing import Process
import threading
import json
import re
import mimetypes
import os
from .http_helpers import *

http_methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'PATCH', 'CONNECT', 'OPTIONS', 'TRACE']
cwd = '/'.join(os.path.realpath(__file__).split('/')[:-2])

def parse_variables(variables, routes, path):
    variables_indexes = {}
    variables_to_replace = {}
    j = 0
    for v in k.split('/'):
        if(re.match('(\([^\)]+\))', v)):
            variables_indexes[j] = v
            variables_to_replace[v] = ''
            k_regex = k.replace(v, '([^\/]+)')
            j = j + 1
        k_regex = '^%s$' % k_regex


def generate_answer(resp, headers, code):
    global codes
    ans = "HTTP/1.1 %s %s\r\n" % (code, codes[code])
    length = len(resp)
    for h in headers:
        ans += "%s: %s\r\n" % (h[0], h[1])

    ans += "Content-Length: %s\r\n" % length
    ans += "Server: SSWeb/0.1\r\n"
    ans += "\r\n"
    ans += resp
    ans += "\n"
    return ans.encode('utf-8')

def parse_http(method, h, body, routes, listen):
    global content_types
    headers = {}
    front_file = ""
    code = 0
    content_type = ""
    data = {}
    method,path,ver = method.split(' ')
    for i in h:
        name, value = i.split(': ')
        headers[name] = value
    vhost = headers['Host']
    path_splitted = path.split('/')
    for r in routes:
        if(vhost in r['domains'] and str(listen) == str(r['listen'])):
            for route in r['routes']:
                for k in route.keys():
                    variables = re.findall('(\([^\)]+\))', k)
                    if len(variables) > 0:
                        variables_indexes = {}
                        variables_to_replace = {}
                        j = 0
                        for v in k.split('/'):
                            if(re.match('(\([^\)]+\))', v)):
                                variables_indexes[j] = v
                                variables_to_replace[v] = ''
                                k_regex = k.replace(v, '([^\/]+)')
                            j = j + 1
                        k_regex = '^%s$' % k_regex
                        if re.search(k_regex, path):
                            for v in variables_indexes:
                                variables_to_replace[variables_indexes[v]] = path_splitted[v]
                            if method in route[k]['methods']:
                                front_file = "%s/views/%s" % (cwd, route[k]['front']['file'])
                                code = route[k]['return']['code']
                                content_type = content_types[route[k]['return']['type']]
                                data = route[k]['front']['data']
                            else:
                                return generate_answer(default_errors[405]['body'], default_errors[405]['headers'], 405)
                    else:
                        if k == path:
                            if method in route[k]['methods']:
                                front_file = "%s/views/%s" % (cwd, route[k]['front']['file'])
                                code = route[k]['return']['code']
                                content_type = content_types[route[k]['return']['type']]
                            else:
                                return generate_answer(default_errors[405]['body'], default_errors[405]['headers'], 405)
                        elif(len(path_splitted) > 2 and path_splitted[1] == "assets"):
                            asset_path = '/'.join(path_splitted[2:])
                            asset_full_path = '%s/assets/%s' % (cwd, asset_path)
                            if os.path.exists(asset_full_path):
                                asset_type = mimetypes.guess_type(asset_full_path)
                                if asset_type is not None:
                                    content_type = asset_type[0]
                                else:
                                    content_type = 'text/plain'
                                front_file = asset_full_path
                                code = 200


    if(code == 0 and front_file == ""):
        return generate_answer(default_errors[404]['body'], default_errors[404]['headers'], 404)
    else:
        f = open(front_file, 'r')
        front_data = f.read()
        f.close()
        to_replace = {}
        for d in data:
            if(data[d] in variables_to_replace.keys()):
                to_replace[d] = variables_to_replace[data[d]]
            front_data = front_data.replace(('((%s))' % d), to_replace[d])
        return generate_answer(front_data, [['Content-Type', content_type]], 200)

def handle_conn(c, addr, listen, routes):
        global http_methods
        print("[*] Connection from: %s:%s" % (addr[0], addr[1]))
        chunks = []
        while True:
            data = c.recv(2048)
            if not data:
                break
            chunks.append(data.replace(b'\r\n', b'\n'))
            if(len(chunks) > 2):
                if(chunks[-1] == b'\n'):
                    break
            else:
                if(chunks[0][-1] == 10):
                    break
        req = (b''.join(chunks)).decode('utf-8')
        print(req.encode('utf-8'))
        hdrs,body = req.split('\n\n', 1)
        headers = hdrs.split('\n')
        method = headers.pop(0)
        allowed_re = '|'.join(http_methods)
        if(re.search((r"(%s)\s(\/\S*)\sHTTP" % allowed_re), method) is not None):
            for h in headers:
                if(re.search('[^\:]+\:\s.*', h) is None):
                   c.send("disallowed requestaa".encode('utf-8'))
                   c.close()
                   return 1
            c.send(parse_http(method, headers, body, routes, listen))
            c.close()
            return 0
        else:
           c.send("disallowed requestbb".encode('utf-8'))
           c.close()
           return 1

def http_server(listen, routes):
    ip,port = listen.split(':')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, int(port)))
    s.listen()
    print("[*] Listening on: %s:%s" % (ip, port))
    while True:
        client, addr = s.accept()

        t = threading.Thread(target=handle_conn, args=(client, addr, listen, routes))
        print("started thread: %s" % t)
        t.start()

def init(listens, r):
    routes = r
    for l in listens:
        p = Process(target=http_server, args=(l,routes))
        print("started process: %s" % p)
        p.start()
