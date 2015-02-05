The main goal of deckr is to provide a protocol for client/server games. To
facilitate this goal, deckr defines the deckr protocol, in addition to the
reference implementation. The deckr protocol exports all functionality
required to interact with games.

Deckr messages are JSON encoded and are terminated by a line break \r\n. Each
message, at the least, must contain a message_type. After this can come an
arbitrary list of key value pairs.

Deckr Message Types
===================

General
-------

* error: Used for a catch all error message.
    * message: A human readable message that describes the problem that was encountered.

Game Management
---------------
These are commands for managing games. This includes functionality such as
seeing all the games a server can provide, creating a new game, destroying a
game, etc.

* list: List all of the games currently available on the server.
* create: Create a new game.
    * game_type_id: The game type to be created.
* destroy
    * game_id: Destroy a specific game.
* list_response: Response to a list command.
    * game_types: A list of game_types. Each game_type is a tuple of
      (human_readable_name, server_id)
* create_response: Indicates that a create was successful.
    * game_id: The game_id of the newly created game
* destroy_response: Indicates that a game was successfully destroyed.
    * game_id: The game_id of the game that was destroyed.

Game commands
-------------
These commands are for interacting with a specific game.

* join: Join a game.
    * game_id: The id of the game to be joined
    * player_id (optional): The player to join as. If present but null will
      create a new player. If not present will join as a spectator.
* join_response: Indicates that the player has joined the game.
    * player_id: The id of the player that is being joined as. null if joined
      as a spectator.
* quit: Quit from the game you are connected to.
* quit_response: Indicate that a player has successfully quit their game.
* game_state
* start
* action
* game_state_response
* game_over
* update
