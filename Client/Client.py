import socket
from threading import Thread
import tkinter


SIZE_Y = 30
SIZE_X = 140


class Client(tkinter.Tk):
    def __init__(self, host, port):
        """
        Create a new Client Object

        :param str host: Server's address
        :param int port: Server's port
        """

        super().__init__()

        self.__host = host
        self.__port = port
        self.__buff = 1024
        self.__sock = socket.socket()

        self.__sock.connect((host, port))

        # Root window
        self.title("TCP Chat")

        # Messages frame
        self.__messages_frame = tkinter.Frame(self)

        # ScrollBar
        self.__scrollbar = tkinter.Scrollbar(self.__messages_frame)

        # Messages
        self.__messages_list = tkinter.Listbox(self.__messages_frame, height=SIZE_Y, width=SIZE_X, yscrollcommand=self.__scrollbar.set)

        # Pack everything up
        self.__scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.__messages_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.__messages_list.pack()
        self.__messages_frame.pack()

        # Message Var
        self.__message = tkinter.StringVar()

        # Message entry
        self.__message_entry = tkinter.Entry(self, textvariable=self.__message)
        self.__message_entry.bind('<Return>', self.send_message)
        self.__message_entry.pack()

        # Send Button
        self.__send_button = tkinter.Button(self, text="Send", command=self.send_message)
        self.__send_button.pack()

        self.protocol("WM_DELETE_WINDOW", self.close)

    def receive(self):
        """
        Receive data sent by the server

        :return:
        """

        try:
            while True:
                data = self.__sock.recv(self.__buff).decode()
                self.__messages_list.insert(tkinter.END, data)
        except ConnectionAbortedError as _:
            self.quit()

    def send_message(self, event=None):
        """
        Method will send the message to the server

        :param event: Sent by binders
        :return:
        """

        msg = self.__message.get().strip()
        print('Trying to send "%s"' % msg)
        if msg == '':
            return
        self.__message.set("")
        self.__sock.send(msg.encode())
        if msg == '/leave':
            self.__sock.close()
            self.quit()

    def close(self, event=None):
        """
        Method closes connection between self and the server
        Notifies the server on disconnection

        :param event: Sent by binders
        :return:
        """

        self.__message.set("/leave")
        self.send_message()


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 1927

    client = Client(HOST, PORT)
    recv_thread = Thread(target=client.receive)
    recv_thread.start()
    tkinter.mainloop()
