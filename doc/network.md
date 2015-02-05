Deckr Engine Networking Layout
==============================

The network in the deckr engine has several components.

* game_master: This is the master endpoint and all clients will need to connect
  to the game master at some point. It acts as something of a router. It
  basically handles games creation, destruction and routing. A game_master
  exposes a very traditional request reply interface.
* game: Each game that is creates a game server. The game server exposes two
  different sockets: a command socket (input) and a broadcast socket (output)
