#!/usr/bin/python

import socket
import select
import time
import sys
import signal
import errno

buffer_size = 4096
delay = 0.0001
forward_to = ('0.0.0.0', int(sys.argv[2]))

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False

class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)
        self.pause = False

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            try:
                inputready, outputready, exceptready = ss(self.input_list, [], [])
                for self.s in inputready:
                    if self.s == self.server:
                        self.on_accept()
                        break

                    self.data = self.s.recv(buffer_size)
                    if len(self.data) == 0:
                        self.on_close()
                    else:
                        self.on_recv()
            except select.error, v:
                print("hi")
                if v[0] != errno.EINTR: 
                    raise
    def set_pause(self):
        self.pause=self.pause==False
    def on_accept(self):
        forward = Forward().start(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()

    def on_close(self):
        print self.s.getpeername(), "has disconnected"
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data        
        if(self.pause):
            time.sleep(int(sys.argv[3]))
        print data
        self.channel[self.s].send(data)

if __name__ == '__main__':
        server = TheServer('0.0.0.0', int(sys.argv[1]))
        def signal_handler(signal, frame):
            print('You paused')
            server.set_pause()
        signal.signal(signal.SIGUSR1, signal_handler)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping server"
            sys.exit(1)