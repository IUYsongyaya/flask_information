from socket import *
import re
import gevent
from gevent import monkey

monkey.patch_all()
import time


def handle_request(service_client_socket):
    """处理请求，包含接收和发送"""
    # print(1)
    request_data = service_client_socket.recv(4096)
    print(2)
    data_list = request_data.decode().split('\r\n')
    print(3)
    request_line = data_list[0]

    obj = re.match(r'\w+\s+(\S+)\s+\S+', request_line)
    request_html = obj.group(1)
    print(request_html, 1)

    if request_html == '/':
        request_html = '/index2.html'

    response_head = 'Host: JIM/1.0\r\n'
    response_line = 'HTTP/1.1 200 OK\r\n'
    try:
        with open('./static' + request_html, 'rb') as file:
            response_body = file.read()
    except:
        with open('static/error.html', 'rb') as file:
            response_body = file.read()

    response_data = (response_line + response_head + '\r\n').encode() + response_body
    service_client_socket.send(response_data)
    service_client_socket.close()


def main():
    time.sleep(0.1)
    tcp_server_socket = socket(AF_INET, SOCK_STREAM)
    tcp_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    ip_port1 = ('', 7878)
    tcp_server_socket.bind(ip_port1)
    tcp_server_socket.listen(128)
    while True:
        print(111111)
        service_client_socket, ip_port2 = tcp_server_socket.accept()
        # handle_request(service_client_socket)
        print(ip_port2, '接通')

        gevent.spawn(handle_request, service_client_socket)
        # print(g1.)
        # time.sleep(0.1)
        # print(g1)


if __name__ == '__main__':
    main()
