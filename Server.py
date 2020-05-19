import socket
from datetime import datetime
from threading import Thread


def print_to_log(message):
    with open('server.log', 'a') as log:
        log.write(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + message + '\n')


class Server:
    def __init__(self, addr=('0.0.0.0', 1927), bufsize=1024, save_log=False):
        self.debug = save_log

        self.__host = addr[0]
        self.__port = addr[1]
        self.__buff = bufsize

        self.__clients = {}

        self.__SERVER = socket.socket()
        self.__SERVER.bind(addr)
        self.__SERVER.listen(1)
        print(str(self))

    def handle_connections(self):
        """
        Method handles incoming connections
        :return:
        """

        while True:
            c_sock, (c_host, c_port) = self.__SERVER.accept()
            self.print("{}:{} has connected".format(c_host, c_port))
            c_sock.send(b"Welcome!")
            c_sock.send(b"Please enter your name.")
            Thread(target=self.handle_client, args=(c_sock,)).start()

    def handle_client(self, sock):
        """
        Method handles clients
        :param socket.socket sock: Client's socket
        :return:
        """

        try:
            name = sock.recv(self.__buff).decode().strip()
            sock.send("Welcome, {}!".format(name).encode())
            self.broadcast_message("%s has joined the server." % name, "SERVER")
            self.__clients[sock] = name

            while True:
                msg = sock.recv(self.__buff)
                self.broadcast_message(msg.decode(), name)
        except ConnectionAbortedError as _:
            sock.close()
            del(self.__clients[sock])
            self.broadcast_message("% has lost connection", "SERVER")

    def broadcast_message(self, msg, pre=None):
        """
        Will send a message to every one connected
        :param str msg: The message
        :param str pre: Prefix (not required)
        :return:
        """
        for sock in self.__clients:
            if pre is not None:
                msg = '[%s] ' % pre + msg.strip()
            self.print(msg)
            sock.send(msg.encode())

    def print(self, msg):
        if self.debug:
            print_to_log(msg)
        print("[{}] {}".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), msg))

    def close(self):
        self.broadcast_message("Server is closing", "SERVER")
        self.__SERVER.close()

    def __str__(self):
        out = 'Server['
        out += '\n\tHOST: ' + self.__host
        out += '\n\tPORT: ' + str(self.__port)
        out += '\n\tBUFF: ' + str(self.__buff)
        out += '\n]'
        return out
