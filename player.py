import pickle

class ManyPlayers(object):
  """A collection of many players."""
  def __init__(self, initial_id=0):
    self._players = []
    self._name_player_map = {}

  def new_player(self, name, password_hash):
    """Create and return a new Player."""
    p = Player(len(self._players), name, password_hash)
    self._players.append(p)
    self._name_player_map[name] = p
    return p

  def get_player_by_id(self, id):
    """Get a Player by id.

    Raises:
      IndexError if the Player doesn't exist.
    """
    if id >= len(self._players):
      raise IndexError('Player with id=%s does not exist.', id)
    return self._players[id]

  def get_player_by_name(self, name):
    """Get a Player by name.

    Raises:
      IndexError if the Player doesn't exist.
    """
    if name not in self._name_player_map:
      raise IndexError('Player %s does not exist.', name)
    return self._name_player_map[name]

  def does_exist_by_name(self, name):
    """Returns whether a player exists with the given name."""
    return name in self._name_player_map

  def does_exist_by_id(self, id):
    """Returns whether a player exists with the given id."""
    return id in self._players

  def save(self, fname):
    """Save players."""
    pickle.dump(fname)

  def load(self, fname):
    """Load players."""
    pickle.load(fname)


class Player(object):
  """A player."""
  def __init__(self, id, name, password_hash):
    self.id = id
    self.name = name
    self.password_hash = password_hash
