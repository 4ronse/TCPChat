import socket
import tkinter
import ctypes
from PIL import Image, ImageTk, ImageOps
from threading import Thread
from colorama import Fore, Back, Style, init

THEME = {
    "mainbackground": "#212121",
    "mainforeground": "#EEFFFF",
    "secondarybackground": "#292929",
    "secondaryforeground": "#f2a365",
    "button": {
        "background": "#393939",
        "foreground": "#EEFFFF"
    }
}

SIZE_Y = 30
SIZE_X = 140


def disable_resize(win):
    """
    https://stackoverflow.com/a/47867275

    :param tkinter.Tk win:
    :return:
    """

    # shortcuts to the WinAPI functionality
    set_window_pos = ctypes.windll.user32.SetWindowPos
    set_window_long = ctypes.windll.user32.SetWindowLongPtrW
    get_window_long = ctypes.windll.user32.GetWindowLongPtrW
    get_parent = ctypes.windll.user32.GetParent

    # The style we want to get back
    GWL_STYLE = -16

    # What we want to subtract from that style
    WS_MINIMIZEBOX = 131072
    WS_MAXIMIZEBOX = 65536

    SWP_NOZORDER = 4
    SWP_NOMOVE = 2
    SWP_NOSIZE = 1
    SWP_FRAMECHANGED = 32

    hwnd = get_parent(win.winfo_id())

    # get old style
    old_style = get_window_long(hwnd, GWL_STYLE)

    # new style
    new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX

    # set new style
    set_window_long(hwnd, GWL_STYLE, new_style)

    # update non-client area (?)
    set_window_pos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)


def get_center_of_screen(master):
    master.update_idletasks()
    pos_x = int(master.winfo_screenwidth() / 2 - master.winfo_reqwidth() / 2)
    pos_y = int(master.winfo_screenheight() / 2 - master.winfo_reqheight() / 2)
    return "+{}+{}".format(pos_x, pos_y)


def set_icon(window):
    """
    Set's icon for given window depending on the os

    :param tkinter.Tk | tkinter.Toplevel window: the window
    :return:
    """
    photo = ImageTk.PhotoImage(file='images/olga.png', master=window)
    window.iconphoto(True, photo)


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

        # Configure Self
        self.title("TCP Chat")
        self.configure(bg=THEME['mainbackground'])
        set_icon(self)
        self.resizable(False, False)
        disable_resize(self)

        # Messages frame
        messages_frame = tkinter.Frame(self)

        # ScrollBar
        scrollbar = tkinter.Scrollbar(messages_frame)

        # Messages
        self.__messages_list = tkinter.Listbox(messages_frame, height=SIZE_Y, width=SIZE_X,
                                               yscrollcommand=scrollbar.set,
                                               bg=THEME['secondarybackground'], fg=THEME['secondaryforeground'])
        self.__messages_list.bind('<<ListboxSelect>>',
                                  lambda event: self.__messages_list.selection_clear(0, tkinter.END))

        # Pack everything up
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.__messages_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.__messages_list.pack()
        messages_frame.pack()

        # Message Var
        self.__message = tkinter.StringVar()

        # Message entry
        message_entry = tkinter.Entry(self, textvariable=self.__message)
        message_entry.bind('<Return>', self.send_message)
        message_entry.pack(padx=20, pady=20, fill=tkinter.X)
        message_entry.focus_set()

        # Send Button
        send_button = tkinter.Button(self, text="Send", command=self.send_message,
                                     bg=THEME['button']['background'],
                                     fg=THEME['button']['foreground'],
                                     borderwidth=0)
        send_button.pack(pady=10)

        # Window Close event
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Geometry
        self.geometry(get_center_of_screen(self))

        # Put Olga on screen
        Olga('NE')  # UP RIGHT
        Olga('SE', flipped=True)  # DOWN RIGHT
        Olga('NW', mirror=True)  # UP LEFT
        Olga('SW', flipped=True, mirror=True)  # DOWN LEFT

    def receive(self):
        """
        Receive data sent by the server

        :return:
        """

        try:
            while True:
                data = self.__sock.recv(self.__buff).decode()
                print(f"{Fore.CYAN}{data}{Style.RESET_ALL}")
                self.__messages_list.insert(tkinter.END, data)
                self.__messages_list.yview(tkinter.END)  # Scroll to the end

        except ConnectionAbortedError as _:
            self.quit()

    def send_message(self, event=None):
        """
        Method will send the message to the server

        :param event: Sent by binders
        :return:
        """

        msg = self.__message.get().strip()
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


class ServerCredentials(tkinter.Tk):
    def __init__(self):
        super().__init__()

        # Configure Self
        self.title("Connect to server")
        self.configure(bg=THEME['mainbackground'])
        set_icon(self)
        self.resizable(False, False)
        disable_resize(self)

        # String vars
        self.stringvar_host = tkinter.StringVar()
        self.stringvar_port = tkinter.StringVar()

        self.stringvar_host.set('127.0.0.1')
        self.stringvar_port.set('1927')

        # Labels
        tkinter.Label(self, text="Host: ", bg=THEME['mainbackground'], fg=THEME['mainforeground']).grid(row=0, pady=2,
                                                                                                        padx=2)
        tkinter.Label(self, text="Port: ", bg=THEME['mainbackground'], fg=THEME['mainforeground']).grid(row=1, pady=2,
                                                                                                        padx=2)

        # Entries
        entry_host = tkinter.Entry(self, textvariable=self.stringvar_host)
        entry_port = tkinter.Entry(self, textvariable=self.stringvar_port)
        entry_host.grid(row=0, column=1, padx=2)
        entry_port.grid(row=1, column=1, padx=2)

        # Set focus on first entry
        entry_host.focus_set()

        # Bindings
        def focus_on_port(event):
            entry_port.focus_set()

        entry_host.bind('<Return>', focus_on_port)
        entry_port.bind('<Return>', self.on_submit)

        # Connect button
        tkinter.Button(self, text="Connect", command=self.on_submit,
                       bg=THEME['button']['background'],
                       fg=THEME['button']['foreground'],
                       borderwidth=0).grid(row=2, column=0, columnspan=3, pady=2)

        # Window Close event
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Geometry
        self.geometry(get_center_of_screen(self))

        # Put Olga on screen
        Olga('NE')  # UP RIGHT
        Olga('SE', flipped=True)  # DOWN RIGHT
        Olga('NW', mirror=True)  # UP LEFT
        Olga('SW', flipped=True, mirror=True)  # DOWN LEFT

    def close(self, event=None):
        self.destroy()
        quit(0)

    def on_submit(self, event=None):
        self.destroy()

    def get_credentials(self):
        return self.stringvar_host.get(), self.stringvar_port.get()


class Olga(tkinter.Toplevel):
    def __init__(self, pos, flipped=False, mirror=False):
        super().__init__()

        # Configure Self
        self.title("Olha :)")
        self.configure(bg=THEME['mainbackground'])
        set_icon(self)
        self.overrideredirect(True)

        # Disable Alt-F4
        def alt_f4_press_event(event):
            self.alt_f4 = True
        self.alt_f4 = False
        self.bind('<Alt-F4>', alt_f4_press_event)
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Image operations
        image = Image.open('images/olga.png')  # Import image

        if mirror:  # Mirror if requested
            image = ImageOps.mirror(image)
        if flipped:  # Flip if requested
            image = ImageOps.flip(image)

        image = image.resize((256, 256), Image.ANTIALIAS)  # Resize image
        image = ImageTk.PhotoImage(image)  # Translate image for tkinter cause he a lil dumb
        label = tkinter.Label(self, image=image)
        label.image = image
        label.pack()

        # Margin
        self.update_idletasks()

        pos = pos.upper()
        if pos == 'NE':
            g = f'+{self.winfo_screenwidth() - self.winfo_width()}+0'
        elif pos == 'SE':
            g = f'+{self.winfo_screenwidth() - self.winfo_width()}+{self.winfo_screenheight() - self.winfo_height()}'
        elif pos == 'NW':
            g = f'+0+0'
        elif pos == 'SW':
            g = f'+0+{self.winfo_screenheight() - self.winfo_height()}'
        else:
            raise ValueError('Unknown position ' + pos)

        self.geometry(g)

    def close(self, event=None):
        if self.alt_f4:
            self.alt_f4 = False
            print('Alt-F4 Detected')
        else:
            self.destroy()


if __name__ == '__main__':
    init()

    connect = ServerCredentials()
    connect.mainloop()
    addr = connect.get_credentials()

    client = Client(addr[0], int(addr[1]))
    recv_thread = Thread(target=client.receive)
    recv_thread.start()
    client.mainloop()
