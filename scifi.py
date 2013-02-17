import signal
import sys
import argparse

import login_manager
import server

def sigint_handler(signal, frame):
  print("[ SIGINT received, exiting ]")
  sys.exit(0)

def launch_server(port):
  # Launch server.
  serv = server.Server(port)
  manager = login_manager.LoginManager(serv)
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
