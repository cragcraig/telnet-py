import server_listener

class LoginManager(server_listener.ServerListener):
  """Manages the login state of players."""
  def __init__(self, server):
    server_listener.ServerListener.__init__(self, server)

  def on_connected(self, connection):
    """Called when a new connection is made."""
    print('%s connected on port %s.' % (connection.addr[0], connection.addr[1]))

  def on_disconnected(self, connection):
    """Called when a connection is lost."""
    print('%s disconnected.' % connection.addr[0])

  def on_read(self, connection, text):
    """Called when a line is read from a connection."""
    print('Client %s: %s' % (connection.addr[0], text))
    connection.write(text.strip('\n'))
    if 'quit' in text:
      connection.disconnect()
    
