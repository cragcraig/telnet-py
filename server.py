import select
import socket


class Connection:

  def  __init__(self, connection, addr):
    self.connection = connection
    self.addr = addr
    self.readbuf = ''
    self.writebuf = ''


class Server:

  def __init__(self, port, backlog=20):
    self._clients = {}
    self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.serv.bind(('', port))
    self.serv.listen(backlog)
    self.serv.setblocking(0)
    self.serv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    self.epoll = select.epoll()
    self.epoll.register(self.serv, select.EPOLLIN | select.EPOLLET)
    print('listening on port %d' % port)

  def accept(self):
    conn, addr = self.serv.accept()
    print('connected to %s:%s' % (addr[0],addr[1]))
    conn.close()
    self.serv.close()

  def poll(self, timeout=-1):
    events = self.epoll.poll(timeout)
    for fileno, event in events:
      # Accept clients
      if fileno == self.serv.fileno():
        try:
          while True:
            conn, addr = self.serv.accept()
            conn.setblocking(0)
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.epoll.register(conn, select.EPOLLIN | select.EPOLLET)
            print('%s joined on port %s' % (addr[0], addr[1]))
            self._clients[conn.fileno()] = Connection(conn, addr)
        except socket.error:
          pass
      # Read client data
      elif event & select.EPOLLIN:
        try:
          while True:
            self._clients[fileno].readbuf +=\
                self._clients[fileno].connection.recv(4096)
        except socket.error:
          pass
      # Write client data
      if event & select.EPOLLOUT:
        try:
          while len(self._clients[fileno].writebuf) > 0:
            bsize = self._clients[fileno].connection.send(
                        self._clients[fileno].writebuf)
            self._clients[fileno].writebuf =\
                self._clients[fileno].writebuf[bsize:]
        except socket.error:
          pass
        if len(self._clients[fileno].writebuf) == 0:
          self.epoll.modify(fileno, select.EPOLLIN | select.EPOLLET)
      # Client disconnect
      if event & select.EPOLLHUP:
        self.epoll.unregister(fileno)
        self._clients[fileno].connection.close()
        print('%s left' % self._clients[fileno].addr[0])
        del self._clients[fileno]

  def write(self, fileno, text):
    self._clients[fileno].writebuf += text
    if '\n' in self._clients[fileno].writebuf:
      self.epoll.modify(fileno,
          select.EPOLLIN | select.EPOLLOUT | select.EPOLLET)

  def read(self, fileno):
    r = self._clients[fileno].readbuf;
    self._clients[fileno].readbuf = ''
    return r

  def readline(self, fileno):
    i = self._clients[fileno].readbuf.find('\n')
    if i < 0:
      return ''
    r = self._clients[fileno].readbuf[:i+1]
    self._clients[fileno].readbuf = self._clients[fileno].readbuf[i+1:]
    return r

  def disconnect(self, fileno):
    self.epoll.modify(fileno, 0)
    self._clients[fileno].connection.shutdown(socket.SHUT_RDWR)

  def clients(self):
    return self._clients.iterkeys()

  def __del__(self):
    self.epoll.unregister(self.serv.fileno())
    self.epoll.close()
    self.serv.shutdown(socket.SHUT_RDWR)
    self.serv.close()
