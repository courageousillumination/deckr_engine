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

Management Commands
-------------------
The deckr server will have a special set of management commands. These allow
you to modify the state of the server. These should generally only run locally.

* authenticate: Authenticate this session with the server
    * secret_key: The secret key you want to authenticate with.
* register_game: Register a new game definition
    * game_definition_path: The path to the game definition.

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
    * game_id: The game_id of the newly created game.
    * game_type_id: The type that was created.
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
* game_state: Request the game state.
* game_state_response: Indicate that the client should set its game state
    * game_state: A list of all items it the game and their attributes.
* start: Start the game. Is also used to indicate to a client that the game has
         started.
* action: Runs a specific action. Takes an number of additional arguments
          which will be passed on to the underlying game in the form of keyword
          arguments. The server will attempt to coerce these into game objects if
          possible.
* update: Indicates to the client that something has happened to the game state.
          The default game provides a couple simple updates all of which are
          specified by 'update_type'
          * set: Sent when some value has changed on an object.
            * game_object: The object that is being modified
            * field: The name of the field that has been changed.
            * value: The new value of the field
          * add: Add the specified object to the zone (it is implicitly
                 removed from the previous zone)
            * game_object: The object to be added to the zone
            * zone: The zone to be added
* game_over
