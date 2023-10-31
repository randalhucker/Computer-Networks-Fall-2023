from message_log import *
import socket
from typing import Tuple

class Group:
    def __init__(self, n, m):
        self.name = n
        self._log = MessageLog()
        self._num_members = m
        
    def new_message(self, user, message):
        """
        This function will add a message to the log.
        """
        self._log.add_message(user, message)
    
    def _new_member(self, user, socket_info: Tuple[socket.socket, str]):
        """
        This function will add a user to the group.
        """
        self._log.add_user(user, socket_info)
    
    def _remove_member(self, user):
        """
        This function will remove a user from the group.
        """
        self._log.remove_user(user)
    
    def get_num_members(self):
        """
        This function will return the number of members in the group.
        """
        return self._num_members

    def join(self, user, socket_info: Tuple[socket.socket, str]):
        """
        This function will add a user to the group.
        """
        self._new_member(user, socket_info)
        self._num_members += 1
        
    def leave(self, user):
        """
        This function will remove a user from the group.
        """
        self._num_members -= 1
    
    def get_all_messages(self):
        """
        This function will return all messages in the log in reverse order. (Newest first)
        """
        return self._log.get_all_messages()
    
    def get_all_users(self):
        """
        This function will return all users in the log.
        """
        return self._log.get_all_users()
    
    def get_last_two_messages(self):
        """
        This function will return the last two messages in the log.
        """
        return self._log.get_last_two_messages()