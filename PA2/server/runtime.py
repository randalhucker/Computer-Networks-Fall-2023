import socket
import threading
import logging
import json
from groups import Group
from typing import Dict, Tuple, List

class Server():
    """This class will handle the server side of the chat application. It will handle multiple clients and will send messages to all connected clients.
    """
    def __init__(self, host='localhost', port=8080):
        self.addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[socket.socket, Tuple[str, str]] = {} # Use a dictionary to store connected clients
        self._logger = logging.getLogger(__name__)
        self._format = "utf-8"
        self.lock = threading.Lock() # Use an instance lock for thread safety
        self.groups: Dict[str, Group] = {"default": Group("default")}
        
    def new_group(self, group_name: str):
        """Adds a group to the server.

        Args:
            group_name (str): The name of the group.
            group (Group): The group object.
        """
        self.groups[group_name] = Group(group_name)
        
    def send_message(self, client: socket.socket, message: dict[str, str], group_name: str = 'default', is_join: bool = False):
        """Sends a message to all connected clients.

        Args:
            client (socket.socket): The client socket.
            message (str): The message to send.
        """
        
        user_name = message['name'] # Get the user's name
        user_message = message['message'] # Get the user's message
        
        if not user_message:
            return  # Skip sending empty messages

        if not is_join:
            with self.lock:
                self.groups[group_name].new_message(message)  # Add the message to the log
            
        json_data = {
            "name": user_name,
            "message": user_message
        }
        json_string = json.dumps(json_data)  # Convert the dictionary to a JSON string
        
        if not is_join:
            for c in self.clients.keys():
                if c != client:
                    self._send_message(c, json_string)  # Send the JSON string to other clients
        else:
            # TODO error here
            self._send_message(client, json_string)  # Send the JSON string to the current client

    
    def _send_message(self, client: socket.socket, dump: str):
        client.sendall(dump.encode(encoding=self._format))
        
    def send_last_two_messages(self, client: socket.socket, group_name: str):
        """Sends the last two messages in the group to the client.

        Args:
            client (socket.socket): The client socket.
        """
        with self.lock:
            last_messages = self.groups[group_name].get_last_two_messages()
            for message in last_messages:
                self.send_message(client, message, group_name, is_join=True)
                
    def join_group(self, client: socket.socket, group_name: str, user_name: str):
        """Adds a client to a group.

        Args:
            client (socket.socket): The client socket.
            group_name (str): The name of the group.
            user_name (str): The name of the user.
        """
        with self.lock:
            _, address = self.clients[client]
            self.groups[group_name].join(user_name, (client, address))
            self.send_last_two_messages(client, group_name)
    
    def get_all_groups(self) -> List[str]:
        """Returns a list of all groups.

        Returns:
            List[str]: A list of all groups.
        """
        return list(self.groups.keys())
    
    def disconnect(self, client: socket.socket, address: str, name: str) -> dict[str, str]:
        self.clients.pop(client)
        user_message = {
            "name" : "CLIENT DISCONNECTED",
            "message" : "Client at address: " + str(address) + " disconnected."
        }
        for group in self.groups.values():
            if group.is_user_in_group(name): # If the user is in the group,
                group.leave(name) # Remove the user from the group
        return user_message
        
    def handle_client(self, client: socket.socket, address):
        """Will handle a client connection. This function will run in a separate thread.

        Args:
            client (socket.socket): The client socket.
            address (str): The address of the client.
        """
        self._logger.info(f"[NEW CONNECTION] {address} connected.") # Log the connection
        # Send an initial message to the client
        initial_msg = {
            "name" : "Server",
            "message" : "Successfully connected to the server."
        }
        initial_msg_string = json.dumps(initial_msg) # Convert the dictionary to a JSON string
        client.send(initial_msg_string.encode(encoding=self._format)) # Send the JSON string
        
        # Send the last 2 messages in the group to the client
        self.send_last_two_messages(client, 'default')
        
        connected = True
        msg = client.recv(1024).decode(self._format) # Receive 1024 bytes of data
        received_json = json.loads(msg) # Convert the JSON string to a dictionary
        user_name = received_json["name"]
        with self.lock:
            self.groups['default'].join(user_name, (client, address))
            self.clients.update({client: [user_name, address]})
        join_msg = {
            "name" : "Server",
            "message" : user_name + " has joined the chat."
        }
        self.send_message(client, join_msg) # Send the message to all connected clients
            
        while connected:
            try:
                user_message_string = client.recv(1024).decode(self._format) # Receive 1024 bytes of data
                
                messages = self.parse_json_string(user_message_string) # Parse the JSON string
                
                for user_message in messages:
                    if not user_message['message']: # If the message is empty,
                        continue # Skip the rest of the loop
                    
                    if user_message['message'] == "disconnect": # If the user wants to disconnect,
                        with self.lock:
                            connected = False
                            user_message = self.disconnect(client, address, user_message['name'])
                    
                    # TODO add a way to change group message from client
                    self.send_message(client, user_message, 'default') # Send the message to all connected clients
            except Exception as e:
                self._logger.error(f"Error handling client: {e}")
        self._logger.info(f"[DISCONNECTION] {address} disconnected.")
        self._logger.info(f"[ACTIVE CONNECTIONS] {len(self.clients)}")
        client.close()
        
    def parse_json_string(self, json_string: str) -> List[Dict[str, str]]:
        # Initialize an empty list to store dictionaries
        parsed_list = []

        # Split the input string into individual JSON objects
        json_objects = json_string.split("}{")
        
        # Handle cases where there are missing curly braces at the beginning or end
        if len(json_objects) > 1:
            json_objects[0] = json_objects[0] + "}"
            json_objects[-1] = "{" + json_objects[-1]

        # Iterate through the JSON objects and parse them
        for obj in json_objects:
            try:
                # Load each JSON object into a dictionary
                parsed_dict = json.loads(obj)
                parsed_list.append(parsed_dict)
            except json.JSONDecodeError:
                # Handle any JSON decoding errors (invalid JSON)
                print(f"Skipping invalid JSON object: {obj}")

        return parsed_list
        
    def start(self):
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow the socket to be reused
            self.socket.bind(self.addr)
            self.socket.listen()
            
            print(f"[LISTENING] Server is listening on {self.addr[0]}:{self.addr[1]}")
            while True:
                client, address = self.socket.accept()
                with self.lock:
                    self.clients[client] = ["", address]
                    thread = threading.Thread(target=self.handle_client, args=(client, address))
                    thread.start()
                    self._logger.info(f"[ACTIVE CONNECTIONS] {len(self.clients)}")
        except KeyboardInterrupt:
            self._logger.info("[SERVER STOPPED] Server stopped by user.")
        except Exception as e:
            self._logger.error(f"Error: {e}")
        finally:
            self.socket.close()
