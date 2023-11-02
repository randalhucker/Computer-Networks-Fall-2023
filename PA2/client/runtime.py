import socket
import threading
import logging
import json
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO)

class Client:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger = logging.getLogger(__name__)
        self._format = "utf-8"
        self.lock = threading.Lock()
        self.name = ""
        self.connected = False

    def send(self, msg: str) -> bool:
        """This method sends a message to the server.

        Args:
            msg (str): The message to send to the server.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        try:
            response_data = {"name": self.name, "message": msg}
            response_string = json.dumps(response_data)
            with self.lock:
                self.socket.sendall(response_string.encode(encoding=self._format))
            return True
        except Exception as e:
            self._logger.error(f"Error sending message: {e}")
            return False

    def recv(self) -> List[Dict[str, str]]:
        """This method receives a message from the server. It will return a list of dictionaries containing the parsed JSON objects.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the parsed JSON objects. Name and message are the keys.
        """
        try:
            json_message_string = self.socket.recv(1024).decode(self._format)
            messages = self.parse_json_string(json_message_string)
            return messages
        except Exception as e:
            self._logger.error(f"Error receiving message: {e}")
            return []

    def receive_messages(self) -> None:
        """Daemon thread that receives messages from the server and prints them to the console. This thread will run until the client disconnects from the server.
        """
        while True:
            try:
                received_msgs = self.recv()
                if not self.connected:
                    break

                with self.lock:
                    for message in received_msgs:
                        if message['message']:
                            print(f"\r[{message['name']}] {message['message']}\n")
                    if not self.name:
                        print("\rEnter name: ", end="")
                    else:
                        print("\rEnter message: ", end="")
            except Exception as e:
                if self.connected:
                    self._logger.error(f"Error receiving message: {e}")

    def parse_json_string(self, json_string: str) -> List[Dict[str, str]]:
        """This method parses a JSON string into a list of dictionaries.

        Args:
            json_string (str): The JSON string to parse.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the parsed JSON objects. Name and message are the keys.
        """
        parsed_list = []
        
        if not json_string:
            return parsed_list

        json_objects = json_string.split("}{")
        
        if len(json_objects) > 1:
            json_objects[0] = json_objects[0] + "}"
            json_objects[-1] = "{" + json_objects[-1]

        for obj in json_objects:
            try:
                parsed_dict = json.loads(obj)
                parsed_list.append(parsed_dict)
            except json.JSONDecodeError:
                self._logger.error(f"Skipping invalid JSON object: {obj}")

        return parsed_list

    def start(self):
        try:
            self.socket.connect(self.addr)
            print(f"[CONNECTED] Connected to server on {self.addr[0]}:{self.addr[1]}")

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            self.connected = True
            while self.connected:
                if not self.name:
                    msg = input("\rEnter name: ")
                    with self.lock:
                        self.name = msg
                        msg = "has connected."
                else:
                    msg = input("\rEnter message: ")
                    if not msg:
                        continue
                if msg.lower() == "disconnect":
                    with self.lock:
                        self.connected = False
                self.send(msg)

        except Exception as e:
            self._logger.error(f"Error: {e}")

        finally:
            print("[DISCONNECTED] Disconnected from server.")
            self.recv()
            self.socket.close()