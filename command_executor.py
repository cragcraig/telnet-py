import commands


class NoSuchCommandError(Exception):
  """No such command error."""
  def __init__(self, command_name):
    super(NoSuchCommandError, self).__init__(
        'Command %s does not exist.' % command_name)

_commands_map = {
  'quit': commands.Quit,
  'echo': commands.Echo,
}

def execute(command_name, connection, player, universe, arg_string):
  if command_name not in _commands_map:
    raise NoSuchCommandError(command_name)
  command = _commands_map[command_name]
  args, kwargs = command.parse_args(arg_string)
  command.run(connection, player, universe, *args, **kwargs)
