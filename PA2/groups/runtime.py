from message_log import *
import socket
from typing import Tuple, Dict

class Group:
    def __init__(self, n: str, og_n:str):
        """
        This function will initialize a group with a name and a message log.
        """
        self.name = n
        self.original_name = og_n
        self._log = MessageLog()
        self._num_members = 0
        
    def new_message(self, message: Dict[str, str]) -> bool:
        """
        This function will add a message to the log.
        """
        try:
            self._log.add_message(message)
            return True
        except Exception:
            return False
    
    def _new_member(self, user: str, socket_info: Tuple[socket.socket, str]) -> bool:
        """
        This function will add a user to the group.
        """
        try:
            self._log.add_user(user, socket_info)
            return True
        except Exception:
            return False
    
    def _remove_member(self, user: str) -> bool:
        """
        This function will remove a user from the group.
        """
        try:
            self._log.remove_user(user)
            return True
        except Exception:
            return False
    
    def get_num_members(self) -> int:
        """
        This function will return the number of members in the group.
        """
        return self._num_members

    def join(self, user: str, socket_info: Tuple[socket.socket, str]) -> bool:
        """
        This function will add a user to the group.
        """
        try:
            self._new_member(user, socket_info)
            self._num_members += 1
            return True
        except Exception:
            return False
        
    def leave(self, user) -> bool:
        """
        This function will remove a user from the group.
        """
        try:
            if self._remove_member(user):
                self._num_members -= 1
                return True
            return False
        except Exception:
            return False
    
    def get_all_messages(self) -> List[Dict[str, str]]:
        """
        This function will return all messages in the log in reverse order. (Newest first)
        """
        return self._log.get_all_messages()
    
    def get_all_users(self) -> Dict[str, Tuple[socket.socket, str]]:
        """
        This function will return all users in the log.
        """
        return self._log.get_all_users()
    
    def get_last_two_messages(self) -> List[Dict[str, str]]:
        """
        This function will return the last two messages in the log.
        """
        return self._log.get_last_two_messages()
    
    def is_user_in_group(self, user: str) -> bool:
        """
        This function will return whether or not a user is in the group.
        """
        return self._log.is_user_in_log(user)
    
    def get_message_by_id(self, id: int) -> Dict[str, str]:
        """
        This function will return a message by its id.
        """
        return self._log.get_message_by_id(id)
    
    def get_original_name(self) -> str:
        """
        This function will return the original name of the group.
        """
        return self.original_name