# TCPChat

This project is a simple tcp chat for my school project in python.

## Setup

First you must have all libraries from the requirements.txt file
installed and figured out.

### Usages

#### Server

```py
server = Server()
server_thread = Thread(target=server.handle_connections)
server_thread.start()
server_thread.join()
server.close()
```

Server also receives parameters:
addr - (tuple) is the address the server should be bonded on
bufsize - (int) how many bytes should the server read each time
save_log - (bool) should logs be saved to a server.log file

#### Client

```py
client = Client(host, port)
recv_thread = Thread(target=client.receive)
recv_thread.start()
tkinter.mainloop()
```

Client receives two parameters:
host - (str) Server's host address
port - (int) Server's port number
