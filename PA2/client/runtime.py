import socket
import threading
import logging
import json


class Client:
    """Client class for connecting to a server.
    """
    def __init__(self, host="localhost", port=8080):
        self.addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger = logging.getLogger(__name__)
        self._format = "utf-8"
        self.lock = threading.Lock()  # Use an instance lock for thread safety
        self.name = ""
        self.connected = False

    def send(self, msg: str) -> None:
        """Will send a message to the server with the client's name and message.

        Args:
            msg (str): The message to send to the server.
        """
        response_data = {"name": self.name, "message": msg} # Create a dictionary
        response_string = json.dumps(response_data) # Convert the dictionary to a JSON string
        with self.lock:
            self.socket.sendall(response_string.encode(encoding=self._format)) # Send the JSON string
            
    def recv(self) -> str:
        """Receives a message from the server.

        Returns:
            str: The message received from the server. JSON formatted.
        """
        try:
            return self.socket.recv(1024).decode(self._format) # Receive 1024 bytes of data
        except Exception as e:
            self._logger.error(f"Error receiving message: {e}")
            return ""

    def receive_messages(self):
        """
        This function will run in a separate thread and will receive messages from the server.
        """
        while True:
            try:
                received_msg = self.recv() # Receive a message from the server
                if not self.connected: # Only print messages if the client is connected
                    break
                with self.lock: # Use a lock to prevent multiple threads from printing at the same time
                    if received_msg: # Only print if the message is not empty
                        print("\r" + " " * 30, end="") # Clear the line
                        received_json = json.loads(received_msg) # Convert the JSON string to a dictionary
                        print(
                            f"\r[{received_json['name']}] {received_json['message']}\n" # Print the message
                        )
                    if self.name == "": # If the client has not set their name, ask them to do so
                        print("\rEnter name: ", end="") 
                    else: # Otherwise, ask them to enter a message
                        print("\rEnter message: ", end="")
            except Exception as e:
                if self.connected:
                    self._logger.error(f"Error receiving message: {e}")

    def start(self):
        """Starts the client and connects to the server.
        """
        try:
            self.socket.connect(self.addr)
            print(f"[CONNECTED] Connected to server on {self.addr[0]}:{self.addr[1]}")

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = (
                True  # Allow the program to exit even if this thread is running
            )
            receive_thread.start()

            self.connected = True
            while self.connected:
                if self.name == "": # If the client has not set their name, ask them to do so
                    msg = input("\rEnter name: ")
                    with self.lock: # Use a lock to prevent multiple threads from printing at the same time
                        self.name = msg
                        msg = "has connected."
                else: # Otherwise, ask them to enter a message
                    msg = input("\rEnter message: ")
                    if msg == "":
                        continue
                if msg == "disconnect":
                    with self.lock:
                        self.connected = False
                self.send(msg)

        except Exception as e:
            self._logger.error(f"Error: {e}")

        finally:
            print("[DISCONNECTED] Disconnected from server.")
            self.recv()
            self.socket.close()
