import command_executor
import commands
import server_listener
import unknown_client


class ConnectionManager(server_listener.ServerListener):
  """Manages mapping connections to players.

  This includes managing the login flow and executing commands.
  """
  _PROMPT = '> '

  def __init__(self, server, many_players):
    server_listener.ServerListener.__init__(self, server)
    self._many_players = many_players
    self._unknown = {}
    self._known = {}
    self._id_connection_map = {}

  def on_connected(self, connection):
    """Called when a new connection is made."""
    player = unknown_client.UnknownClient(self._many_players)
    self._unknown[connection] = player
    player.update(connection)

  def on_disconnected(self, connection):
    """Called when a connection is lost."""
    print('%s disconnected.' % connection.addr[0])
    if connection in self._unknown:
      del self._unknown[connection]
    if connection in self._known:
      id = self._known[connection].id
      if self._id_connection_map[id] == connection:
        del self._id_connection_map[id]
      del self._known[connection]

  def on_read(self, connection, text):
    """Called when a line is read from a connection."""
    if connection in self._unknown:
      # Unknown client.
      p = self._unknown[connection].update(connection, text)
      if p:
        if p.id in self._id_connection_map:
          old_connection = self._id_connection_map[p.id]
          old_connection.write('You have logged in from another location.')
          old_connection.disconnect()
        self._id_connection_map[p.id] = connection
        self._known[connection] = p
        del self._unknown[connection]
        connection.prompt()
    else:
      # Known client:
      p = self._known[connection]
      try:
        tmp = text.split(None, 1)
        cmd = tmp[0] if len(tmp) > 0 else ''
        args_str = tmp[1] if len(tmp) > 1 else ''
        command_executor.execute(cmd, connection, p, None, args_str)
      except (command_executor.NoSuchCommandError, commands.UsageError) as e:
        connection.write(str(e))
      connection.prompt()
