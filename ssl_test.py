import socket
import ssl

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 8082))
s.listen(5)

while True:
    client,addr = s.accept()
    ss = ssl.wrap_socket(client, server_side=True, ca_certs='./ssl/rootCA.crt', certfile='./ssl/domain.crt', keyfile='./ssl/domain.key')
    print("[*] Connection from: %s:%s" % (addr[0], addr[1]))
    try:
        data = ss.recv(2048)
        print("[*] Received: %s" % data)
        ss.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\n\r\nOK\r\n".encode('utf-8'))
        ss.close()
    except:
        print("ssl error")
