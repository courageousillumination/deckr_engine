"""
A very simple Client for testing the networking portions of deckr.
"""

class Client(object):

    def connect(self, target):
        pass

    def disconnect(self, target):
        pass

    def send_command(self, command_name, **kwargs):
        pass

    def wait_for_response(self):
        """
        Waits for a response and returns that value.
        """
        
        pass
