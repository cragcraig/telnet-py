import select
import socket


class Connection(object):
  """A single client connection."""
  def  __init__(self, connection, addr, server):
    self.connection = connection
    self.addr = addr
    self._server = server
    self._readbuf = ''
    self._writebuf = ''
    self.writebuf_out = ''
    self.read_queue = []

  def __hash__(self):
    return self.connection.fileno()

  def __eq__(self, other):
    return self.__hash__() == other.__hash__()

  def __ne__(self, other):
    return not self.__eq__(other)

  def append_read(self, text):
    """Add some text to the read buffer."""
    self._readbuf += text
    while '\n' in self._readbuf:
      i = self._readbuf.find('\n')
      self.read_queue.append(self._readbuf[:i+1].strip('\r\n '))
      self._readbuf = self._readbuf[i+1:]

  def write(self, text, end='\n'):
    """Write some text to the connection."""
    self._writebuf += text + end
    while '\n' in self._writebuf:
      i = self._writebuf.find('\n')
      self.writebuf_out += self._writebuf[:i+1]
      self._writebuf = self._writebuf[i+1:]
      self._server.request_write(self.connection.fileno())

  def flush(self):
    """Write the current writebuf immediately."""
    self.writebuf_out += self._writebuf
    self._writebuf = ''
    self._server.request_write(self.connection.fileno())

  def prompt(self, prompt):
    """Write a prompt to writebuf."""
    self.write(prompt, end='')
    self.flush()

  def readline(self):
    """Get a line that received by the connection."""
    if self.read_queue:
      return self.read_queue.pop(0)
    return None

  def iter_read(self):
    """Iterate through lines received by the connection."""
    while self.read_queue:
      yield self.read_queue.pop(0)

  def disconnect(self):
    """Disconnect this connection."""
    self._server.disconnect(self.connection.fileno())


class Server(object):
  """Handles all socket connections."""
  def __init__(self, port, backlog=20):
    self._listeners = []
    self._clients = {}
    self._to_disconnect = []
    self.epoll = None
    self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.serv.bind(('', port))
    self.serv.listen(backlog)
    self.serv.setblocking(0)
    self.serv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    self.epoll = select.epoll()
    self.epoll.register(self.serv, select.EPOLLIN | select.EPOLLET)
    print('listening on port %d.' % port)

  def add_listener(self, listener):
    if listener not in self._listeners:
      self._listeners.append(listener)

  def remove_listener(self, listener):
    try:
      self._listeners.remove(listener)
    except ValueError:
      pass

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
            print('%s connected on port %s.' % (addr[0], addr[1]))
            connection = Connection(conn, addr, self)
            self._clients[conn.fileno()] = connection
            for li in self._listeners:
              li.on_connected(connection)
        except socket.error:
          pass
      # Read client data
      elif event & select.EPOLLIN:
        try:
          while True:
            self._clients[fileno].append_read(
                self._clients[fileno].connection.recv(4096))
            for l in self._clients[fileno].iter_read():
              for li in self._listeners:
                li.on_read(self._clients[fileno], l)
        except socket.error:
          pass
      # Write client data
      if event & select.EPOLLOUT:
        try:
          while len(self._clients[fileno].writebuf_out) > 0:
            bsize = self._clients[fileno].connection.send(
                        self._clients[fileno].writebuf_out)
            self._clients[fileno].writebuf_out = (
                self._clients[fileno].writebuf_out[bsize:])
        except socket.error:
          pass
        if len(self._clients[fileno].writebuf_out) == 0:
          self.epoll.modify(fileno, select.EPOLLIN | select.EPOLLET)
      # Client disconnect
      if event & select.EPOLLHUP:
        self.epoll.unregister(fileno)
        self._clients[fileno].connection.close()
        print('%s disconnected.' % self._clients[fileno].addr[0])
        for li in self._listeners:
          li.on_disconnected(connection)
        del self._clients[fileno]
      # Disconnect pending clients
      self._disconnect_pending()

  def request_write(self, fileno):
    self.epoll.modify(fileno,
        select.EPOLLIN | select.EPOLLOUT | select.EPOLLET)

  def disconnect(self, fileno):
    if fileno not in self._to_disconnect:
      self._to_disconnect.append(fileno)

  def _disconnect_pending(self):
    for fileno in self._to_disconnect[:]:
      if fileno not in self._clients:
        self._to_disconnect.remove(fileno)
      elif len(self._clients[fileno].writebuf_out) == 0:
        self._disconnect_internal(fileno)
        self._to_disconnect.remove(fileno)

  def _disconnect_internal(self, fileno):
    self.epoll.modify(fileno, 0)
    self._clients[fileno].connection.shutdown(socket.SHUT_RDWR)
    for li in self._listeners:
      li.on_disconnected(self._clients[fileno])
    del self._clients[fileno]

  def iter_clients(self):
    return self._clients.iterkeys()

  def __del__(self):
    if self.epoll:
      self.epoll.unregister(self.serv.fileno())
      self.epoll.close()
      self.serv.shutdown(socket.SHUT_RDWR)
      self.serv.close()
