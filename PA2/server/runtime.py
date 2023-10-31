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
        self.clients: Dict[socket.socket, str] = {} # Use a dictionary to store connected clients
        self._logger = logging.getLogger(__name__)
        self._format = "utf-8"
        self.lock = threading.Lock() # Use an instance lock for thread safety
        self.default_group = Group("default", 0)
        
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
        connected = True
        msg = client.recv(1024).decode(self._format) # Receive 1024 bytes of data
        received_json = json.loads(msg) # Convert the JSON string to a dictionary
        user_name = received_json["name"]
        self.default_group.join(user_name, (client, address))
        while connected:
            try:
                msg = client.recv(1024).decode(self._format) # Receive 1024 bytes of data
                received_json = json.loads(msg) # Convert the JSON string to a dictionary
                user_name = received_json["name"]
                user_message = received_json["message"]
                with self.lock:
                    self.default_group.new_message(user_name, user_message)
                
                # Test group methods
                print("Number of members: ", self.default_group.get_num_members())
                all_messages = self.default_group.get_all_messages()
                for message in all_messages:
                    print(message)
                print(self.default_group.get_last_two_messages())
                
                if not msg: # If the message is empty,
                    continue
                if user_message == "disconnect": # If the user wants to disconnect,
                    connected = False
                    self.clients.pop(client)
                    user_message = "[CLIENT DISCONNECTED] Client on address: " + str(address) + " disconnected."
                for c, (name, addr) in self.clients.items(): # Iterate through all connected clients
                    if c != client: # If the client is not the current client,
                        json_data = { # Create a dictionary
                            "name": user_name,
                            "message": user_message
                        }
                        json_string = json.dumps(json_data) # Convert the dictionary to a JSON string
                        c.sendall(json_string.encode(encoding=self._format)) # Send the JSON string
            except Exception as e:
                self._logger.error(f"Error handling client: {e}")
                break
        self._logger.info(f"[DISCONNECTION] {address} disconnected.")
        self._logger.info(f"[ACTIVE CONNECTIONS] {len(self.clients)}")
        client.close()
        
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
