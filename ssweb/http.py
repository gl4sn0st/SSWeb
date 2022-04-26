import socket
from multiprocessing import Process
import threading
import json
import re

http_methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'PATCH', 'CONNECT', 'OPTIONS', 'TRACE']
codes = {
100: 'Continue',
101: 'Switching protocols',
102: 'Processing',
103: 'Early Hints',
200: 'OK',
201: 'Created',
202: 'Accepted',
203: 'Non-Authoritative Information',
204: 'No Content',
205: 'Reset Content',
206: 'Partial Content',
207: 'Multi-Status',
208: 'Already Reported',
226: 'IM Used',
300: 'Multiple Choices',
301: 'Moved Permanently',
302: 'Found',
303: 'See Other',
304: 'Not Modified',
305: 'Use Proxy',
306: 'Switch Proxy',
307: 'Temporary Redirect',
308: 'Permanent Redirect',
400: 'Bad Request',
401: 'Unauthorized',
402: 'Payment Required',
403: 'Forbidden',
404: 'Not Found',
405: 'Method Not Allowed',
406: 'Not Acceptable',
407: 'Proxy Authentication Required',
408: 'Request Timeout',
409: 'Conflict',
410: 'Gone',
411: 'Length Required',
412: 'Precondition Failed',
413: 'Payload Too Large',
414: 'URI Too Long',
415: 'Unsupported Media Type',
416: 'Range Not Satisfiable',
417: 'Expectation Failed',
418: 'I\'m a Teapot',
421: 'Misdirected Request',
422: 'Unprocessable Entity',
423: 'Locked',
424: 'Failed Dependency',
425: 'Too Early',
426: 'Upgrade Required',
428: 'Precondition Required',
429: 'Too Many Requests',
431: 'Request Header Fields Too Large',
451: 'Unavailable For Legal Reasons',
500: 'Internal Server Error',
501: 'Not Implemented',
502: 'Bad Gateway',
503: 'Service Unavailable',
504: 'Gateway Timeout',
505: 'HTTP Version Not Supported',
506: 'Variant Also Negotiates',
507: 'Insufficient Storage',
508: 'Loop Detected',
510: 'Not Extended',
511: 'Network Authentication Required'
}

content_types = {
    'html': 'text/html'
}

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
                            path_splitted = path.split('/')
                            for v in variables_indexes:
                                variables_to_replace[variables_indexes[v]] = path_splitted[v]
                            if method in route[k]['methods']:
                                front_file = route[k]['front']['file']
                                code = route[k]['return']['code']
                                content_type = content_types[route[k]['return']['type']]
                                data = route[k]['front']['data']
                            else:
                                return generate_answer('ERROR', [['Content-Type', 'text/plain']], 405)
                    else:
                        if k == path:
                            if method in route[k]['methods']:
                                front_file = route[k]['front']['file']
                                code = route[k]['return']['code']
                                content_type = content_types[route[k]['return']['type']]
                            else:
                                return generate_answer('ERROR', [['Content-Type', 'text/plain']], 405)

    if(code == 0 and front_file == ""):
        return generate_answer('ERROR', [['Content-Type', 'text/plain']], 404)
    else:
        f = open(('/Users/glasn0st/Documents/projects/web/views/%s' % front_file), 'r')
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
            c.send(parse_http(method, headers, body, routes, listen))
            c.close()
        else:
           c.send("disallowed requestbb".encode('utf-8'))
           c.close()

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
