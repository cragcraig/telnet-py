
class UsageError(Exception):
  """Usage error."""
  def __init__(self, command_cls):
    super(UsageError, self).__init__('Usage: %s' % command_cls.usage())


class BaseCommand(object):
  """Base class for all commands."""
  def __init__(self):
    raise NotImplementedError('Commands should not be instantiated.')

  @staticmethod
  def help():
    """Get a help string.

    Returns:
      Help string.
    """
    return 'No help avaliable for this command.'

  @staticmethod
  def usage():
    """Print a usage string.

    Returns:
      Usage string.
    """
    return ''

  @staticmethod
  def parse_args(arg_string):
    """Parse the argument string.

    Returns:
      Tuple ([args], {kwargs})
    """
    return ([], {})

  @staticmethod
  def run(connection, player, universe):
    """Run the command."""
    raise NotImplementedError('Abstract base class, override the run() method.')


class Quit(BaseCommand):
  @staticmethod
  def help():
    return 'Disconnect the current session.'

  @staticmethod
  def run(connection, player, universe):
    connection.disconnect()


class Echo(BaseCommand):
  @staticmethod
  def help():
    return 'Echo the given text.'

  @staticmethod
  def parse_args(arg_string):
    return ([arg_string], {})

  @staticmethod
  def run(connection, player, universe, text):
    connection.write(text)
