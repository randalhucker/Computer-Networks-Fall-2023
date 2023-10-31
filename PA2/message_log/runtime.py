from typing import Dict, Tuple, List
import socket

class MessageLog():
    """
    This class will handle storing all of the server's information.
    """
    
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.users: Dict[str, Tuple[socket.socket, str]] = {}
    
    def add_message(self, user, message):
        """
        This function will add a message to the log.
        """
        self.messages.append({"name": user, "message": message})
        
    def add_user(self, user, socket_info):
        """
        This function will add a {User: Addr} to the log.
        """
        self.users[user] = socket_info
    
    def remove_user(self, user):
        """
        This function will remove a user from the log.
        """
        self.users.pop(user)
        
    def get_all_messages(self):
        """
        This function will return all messages in the log in reverse order. (Newest first)
        """
        reversed = self.messages.reverse()
        return reversed
    
    def get_all_users(self):
        """
        This function will return all users in the log.
        """
        return self.users
    
    def get_last_two_messages(self):
        """
        This function will return the last two messages in the log.
        """
        try:
            return self.messages[-2:]
        except IndexError:
            try:
                return self.messages[-1:]
            except IndexError:
                return []
        
    