import signal
import socket
import sys
from select import epoll

import server

def sigint_handler(signal, frame):
  print("SIGINT")
  sys.exit(0)

def main():
  signal.signal(signal.SIGINT, sigint_handler)
  if len(sys.argv) != 2:
    print("usage: scifi PORT")
    return
  else:
    port = int(sys.argv[1])

  serv = server.Server(port)
  serv.accept()

if __name__ == "__main__":
  main()

