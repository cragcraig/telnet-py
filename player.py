import pickle

class ManyPlayers(object):
  """A collection of many players."""
  def __init__(self, initial_id=0):
    self._players = []
    self._name_player_map = {}

  def new_player(name):
    """Create and return a new Player."""
    p = Player(len(self._players), name)
    self._players.append(p)
    self._name_player_map[name] = p
    return p

  def get_player_by_id(id):
    """Get a Player by id.

    Raises:
      IndexError if the Player doesn't exist.
    """
    if id >= len(self._players):
      raise IndexError('Player id=%s doesn\'t exist.', id)
    return self._players[id]

  def get_player_by_name(name):
    """Get a Player by name.

    Raises:
      IndexError if the Player doesn't exist.
    """
    if name not in self._name_player_map:
      raise IndexError('Player name=%s doesn\'t exist.', name)
    return self._name_player_map[name]

  def save(fname):
    """Save players."""
    pickle.dump(fname)

  def load(fname):
    """Load players."""
    pickle.load(fname)


class Player(object):
  """A player."""
  def __init__(self, id, name):
    self.id = id
    self.name = name
