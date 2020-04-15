from socket import *
from select import select
import re


# 主体功能

class HTTPsever:
    def __init__(self, host="0.0.0.0", port=0000, html=None):
        self.host = host
        self.port = port
        self.html = html
        self.create_socket()
        self.bind()
        self.rlist = []  # 初始关注监听套接字的读行为,s为客户端连接,属于读事件.
        self.wlist = []
        self.xlist = []

    def create_socket(self):
        self.tcp_socket = socket()
        self.tcp_socket.setblocking(False)

    def bind(self):
        self.address = (self.host, self.port)
        self.tcp_socket.bind(self.address)

    def start(self):
        self.tcp_socket.listen(3)
        print("listen the port is %s" % self.port)
        # 完成select并发
        self.rlist.append(self.tcp_socket)
        while True:
            # 对IO进行监控
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            # 遍历rs列表分情况讨论
            for r in rs:  # 一个s可以应对多个c(客户端套接字)
                # 监听套接字就绪
                if r is self.tcp_socket:
                    c, addr = r.accept()
                    print("Connect from", addr)
                    # 添加客户端连接套接字作为监控对象
                    c.setblocking(False)
                    # 把客户端连接套接字添加到监控rlist列表中（但是没有删除）
                    self.rlist.append(c)
                else:
                    request = r.recv(1024).decode()
                    print(request)
                    pattern = r"[A-Z]+\s+(/\S*)"
                    try:
                        info = re.match(pattern, request).group(1)
                    except:
                        self.rlist.remove(r)
                        r.close()
                        return
                    else:
                        self.get_html(r, info)

    def get_html(self, r, info):
        if info == "/":
            filename = self.html + "/index.html"
        else:
            filename = self.html +info
        try:
            file = open(filename,"rb")
        except:
            response_headers ="HTTP/1.1 404 NOT FOUND\r\n"
            response_headers +="Content-Type:text.html\r\n"
            response_headers +="\r\n"
            response_content ="<h1>sorry......</h1>"
            response = (response_headers+response_content).encode()
        else:
            response_content = file.read()
            response_headers = "HTTP/1.1 200 OK\r\n"
            response_headers += "Content-Type:text.html\r\n"
            response_headers += "Content-Length:%d\r\n"%len(response_content)
            response_headers += "\r\n"
            response = response_headers.encode() + response_content
            file.close()
        finally:
            r.send(response)

if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8006
    dir = "./static"
    httpd = HTTPsever(host=host, port=port, html=dir)
    httpd.start()
