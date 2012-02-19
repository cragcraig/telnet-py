import socket

class Server:

  def __init__(self, port, backlog=5):
    self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.serv.bind(('localhost', port))
    self.serv.listen(backlog)
    print('listening on port %d' % port)

  def accept(self):
    conn, addr = self.serv.accept()
    print('connected to %s:%s' % (addr[0],addr[1]))
    conn.send('Hello World!\n')
    conn.close()
    self.serv.close()
