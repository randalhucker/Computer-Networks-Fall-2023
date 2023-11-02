from typing import Dict, Tuple, List
import socket

class MessageLog():
    """
    This class will handle storing all of the server's information.
    """
    
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.users: Dict[str, Tuple[socket.socket, str]] = {}
        self.blank_message = {
            "name": "",
            "message": "",
            "id": ""
        }
    
    def add_message(self, message: Dict[str, str]):
        """
        This function will add a message to the log.
        """
        message['id'] = len(self.messages) + 1
        self.messages.append(message)
        
    def add_user(self, user, socket_info: Tuple[socket.socket, str]):
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
        return list(reversed(self.messages))
    
    def get_all_users(self):
        """
        This function will return all users in the log.
        """
        return self.users
    
    def is_user_in_log(self, user: str) -> bool:
        """
        This function will return True if the user is in the log.
        """
        return user in self.users

    def get_message_by_id(self, id: int) -> Dict[str, str]:
        """
        This function will return a message by its id.
        """
        for message in self.messages:
            if message['id'] == id:
                return message
        return self.blank_message
    
    def get_last_two_messages(self) -> List[Dict[str, str]]:
        """
        This function will return the last two messages in the log.
        """
        all_messages = self.get_all_messages()
        try:
            return [all_messages[1], all_messages[0]]
        except IndexError:
            try:
                return [self.blank_message, all_messages[0]]
            except IndexError:
                return [self.blank_message, self.blank_message]
        
    