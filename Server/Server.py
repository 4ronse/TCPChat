import os
import socket
from datetime import datetime
from threading import Thread


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


# TODO: Implement commands


def print_to_log(message):
    """
    Methods puts given message into the server.log file
    :param str message: debug message
    :return:
    """

    with open(os.path.join(ROOT_PATH, 'server.log'), 'a') as log:
        log.write(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + message + '\n')


def get_motd() -> list:
    try:
        with open(os.path.join(ROOT_PATH, 'motd.txt'), 'r') as motd:
            x = motd.read()
        x = x.splitlines()
        return x
    except FileNotFoundError as _:
        return []


class Server:
    def __init__(self, addr=('0.0.0.0', 1927), bufsize=1024, save_log=False):
        """
        Create a new Server Object

        :param tuple addr: Server's address
        :param int bufsize: Server's buffer size
        :param bool save_log: Save log to server.log
        """

        self.debug = save_log

        self.__host = addr[0]
        self.__port = addr[1]
        self.__buff = bufsize

        self.__clients = {}
        self.__addresses = {}

        self.__SERVER = socket.socket()
        self.__SERVER.bind(addr)
        self.__SERVER.listen(1)
        print(str(self))
        print()

    def handle_connections(self):
        """
        Method handles incoming connections

        :return:
        """

        while True:
            c_sock, c_addr = self.__SERVER.accept()
            self.__addresses[c_sock] = c_addr
            self.print("{}:{} has connected".format(c_addr[0], c_addr[1]))
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
            for l in get_motd():
                sock.send(l.encode())
            self.broadcast_message("%s has joined the server." % name, "SERVER")
            self.__clients[sock] = name

            while True:
                msg = sock.recv(self.__buff).decode().strip()

                if msg == '':
                    pass
                elif msg == '/leave':
                    sock.close()
                    del self.__clients[sock]
                    self.broadcast_message("{} left the server".format(name), "SERVER")
                    return
                else:
                    self.broadcast_message(msg, name)
        except ConnectionResetError or ConnectionAbortedError as _:
            try:
                temp = self.__clients[sock]
                sock.close()
                del self.__clients[sock]
                self.broadcast_message("{} has lost connection".format(temp), "SERVER")
            except KeyError as _:
                addr = self.__addresses[sock]
                self.print("{}:{} connection aborted".format(addr[0], addr[1]))
            finally:
                del self.__addresses[sock]

    def broadcast_message(self, msg, pre=None):
        """
        Will send a message to every one connected

        :param str msg: The message
        :param str pre: Prefix (not required)
        :return:
        """
        if pre is not None:
            msg = '[%s] ' % pre + msg.strip()

        self.print(msg)
            
        for sock in self.__clients:
            sock.send(msg.encode())

    def print(self, msg):
        """
        Method will print given message to console
        If server is set to save log, method will also
        print given message to log.

        :param str msg: The message
        :return:
        """

        if self.debug:
            print_to_log(msg)
        print("[{}] {}".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), msg))

    def close(self):
        """
        Method stops the server.

        :return:
        """
        self.broadcast_message("Server is closing", "SERVER")
        self.__SERVER.close()

    def __str__(self):
        out = 'Server ['
        out += '\n\tHOST: ' + self.__host
        out += '\n\tPORT: ' + str(self.__port)
        out += '\n\tBUFF: ' + str(self.__buff)
        out += '\n]'
        return out


if __name__ == '__main__':
    server = Server(save_log=True)

    server_thread = Thread(target=server.handle_connections)
    server_thread.start()
    server_thread.join()
    server.close()
