import socket

class PrologixGPIBConnection:
    def __init__(self, ip_address):
        self.host=ip_address
        self.port=1234
        self.sock=None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        return self.sock.connect((self.host,self.port))

    def disconnect(self):
        if not (self.sock is None):
            self.sock.close()
            self.sock=None

    def send_message(self,gpib_address,command):
        message="++addr {}\n".format(gpib_address)
        self.sock.sendall(message.encode())
        message="{}\n".format(command)  #WARNING this assumes the end of message character is \n, will need to check
        self.sock.sendall(message.encode())

    def read(self,end_of_message_character=10):
        data=self.sock.recv(1024)
        while len(data)==0 or data[-1]!=end_of_message_character:
            data+=self.sock.recv(1024)
        return data
    
    def __del__(self):
        self.disconnect()
