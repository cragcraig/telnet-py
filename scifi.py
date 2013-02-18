import signal
import sys
import argparse

import connection_manager
import player
import server

def sigint_handler(signal, frame):
  print("[ SIGINT received, exiting ]")
  sys.exit(0)

def launch_server(port):
  # Launch server.
  serv = server.Server(port)
  players = player.ManyPlayers()
  manager = connection_manager.ConnectionManager(serv, players)
  while True:
    serv.poll()

if __name__ == "__main__":
  signal.signal(signal.SIGINT, sigint_handler)
  # Usage and arguments.
  parser = argparse.ArgumentParser(description='Telnet server.')
  parser.add_argument('port', metavar='PORT', type=int,
                      help='port to listen for client connections')
  args = parser.parse_args()
  launch_server(args.port)
