class ServerListener(object):
  """An interface for listening to the server."""
  def __init__(self, server):
    self._server = server
    self.start_listening()

  def start_listening(self):
    self._server.add_listener(self)

  def stop_listening(self):
    self._server.remove_listener(self)
    self._server = None

  def on_connected(self, connection):
    """Called when a new connection is made."""
    raise NotImplementedError

  def on_disconnected(self, connection):
    """Called when a connection is lost."""
    raise NotImplementedError

  def on_read(self, connection, text):
    """Called when a line is read from a connection."""
    raise NotImplementedError
